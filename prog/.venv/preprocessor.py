import subprocess
import importlib
import sys
import logging
from transformers import BaseImageProcessorFast
import torch
import numpy as np
from rembg import remove, new_session
from functools import partial
from torchvision.utils import save_image
from PIL import Image
from kiui.op import recenter
import kiui


# commented out the package installation part as it's not necessary for this fix
# and might be causing issues if run repeatedly


class LRMImageProcessor(BaseImageProcessorFast):
    def __init__(self, source_size=512, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_size = source_size
        self.session = None
        self.rembg_remove = None

    # we define _initialize_session here to avoid "pickle onnx" problem
    def _initialize_session(self):
        if self.session is None:
            self.session = new_session("isnet-general-use")
            self.rembg_remove = partial(remove, session=self.session)

    def preprocess_image(self, image):
        self._initialize_session()
        image = np.array(image)
        image = self.rembg_remove(image)
        mask = self.rembg_remove(image, only_mask=True)
        image = recenter(image, mask, border_ratio=0.20)
        image = torch.tensor(image).permute(2, 0, 1).unsqueeze(0) / 255.0
        if image.shape[1] == 4:
            image = image[:, :3, ...] * image[:, 3:, ...] + (1 - image[:, 3:, ...])
        image = torch.nn.functional.interpolate(image, size=(self.source_size, self.source_size), mode='bicubic', align_corners=True)
        image = torch.clamp(image, 0, 1)
        return image

    def get_normalized_camera_intrinsics(self, intrinsics: torch.Tensor):
        fx, fy = intrinsics[:, 0, 0], intrinsics[:, 0, 1]
        cx, cy = intrinsics[:, 1, 0], intrinsics[:, 1, 1]
        width, height = intrinsics[:, 2, 0], intrinsics[:, 2, 1]
        fx, fy = fx / width, fy / height
        cx, cy = cx / width, cy / height
        return fx, fy, cx, cy

    def build_camera_principle(self, RT: torch.Tensor, intrinsics: torch.Tensor):
        fx, fy, cx, cy = self.get_normalized_camera_intrinsics(intrinsics)
        return torch.cat([
            RT.reshape(-1, 12),
            fx.unsqueeze(-1),
            fy.unsqueeze(-1),
            cx.unsqueeze(-1),
            cy.unsqueeze(-1),
        ], dim=-1)

    def _default_intrinsics(self):
        fx = fy = 384
        cx = cy = 256
        w = h = 512
        intrinsics = torch.tensor([
            [fx, fy],
            [cx, cy],
            [w, h],
        ], dtype=torch.float32)
        return intrinsics

    def _default_source_camera(self, batch_size: int = 1):
        dist_to_center = 1.5
        canonical_camera_extrinsics = torch.tensor([[
            [0, 0, 1, 1],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ]], dtype=torch.float32)
        canonical_camera_intrinsics = self._default_intrinsics().unsqueeze(0)
        source_camera = self.build_camera_principle(canonical_camera_extrinsics, canonical_camera_intrinsics)
        return source_camera.repeat(batch_size, 1)

    def __call__(self, image, *args, **kwargs):
        processed_image = self.preprocess_image(image)
        source_camera = self._default_source_camera(batch_size=1)
        return processed_image, source_camera