import flet as ft
import os

from generation import generate_3d
from generate_2d import generate_im


def main(page: ft.Page):
    
    page.title = "3D-generation (blender)"
    page.theme_mode = 'dark'
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
   
    page.window.width = 800
    page.window.height = 800
    page.window.alignment = ft.Alignment(0.0, 0.0)
    

    def change_theme(e):
        page.theme_mode = 'light' if page.theme_mode == 'dark' else 'dark'
        page.update()
    
    
    change_theme_btn = ft.IconButton(ft.Icons.WB_SUNNY_ROUNDED, on_click= change_theme)

    # страница для текст-2d
    

    def us_d_len(e):
        user_prmt.counter_text = f'колличество символов: {len(user_prmt.value)}'
        get_btn_t.disabled = False if len(user_prmt.value) > 0 else True
        
        page.update()


    def get_im_t(e):
        prmt = user_prmt.value
        
        get_btn_t.disabled = True
        page.navigation_bar.disabled = True
        dscrpt_t.value = 'В процессе генерации...'
        page.update()
        
        try:
            path_to_im = generate_im(prmt)
            
            if path_to_im:
        
                page.set_clipboard(path_to_im)
                dscrpt_t.value  = f'Готово, путь до картинки скопирован в буфер обмена.'

                generated_im.src =  path_to_im
                generated_im.visible = True
            
                peredelat_btn.visible = True
                peredelat_btn.disabled = False
            
                page.update()

            else:
                dscrpt_t.value  = f'Проблемы с интернетом!'
            
        
        except Exception as k:
            dscrpt_t.value  = f"""Произошла ошибка:
            {k}"""
            
        get_btn_t.disabled = False
        page.navigation_bar.disabled = False
        page.update()
    

    def get_im_t_peredel(e):
        generated_im.visible = False
            
        peredelat_btn.visible = False
        peredelat_btn.disabled = True
        
        path_to_im = generated_im.src
        
        generated_im.src= None
        
        os.remove(path_to_im)
        dscrpt_t.value = ''
        
        page.update()


    generated_im = ft.Image(
        src = f"/icons/icon-512.png",
        width=250,
        height=250,
        fit= ft.ImageFit.CONTAIN,
        visible= False
        )


    user_prmt = ft.TextField(
        label= 'Введите текст',
        width=400,
        on_change= us_d_len,
        counter_text='колличество символов: 0',
        text_align= ft.TextAlign.CENTER)


    dscrpt_t = ft.Text('')
    
    get_btn_t = ft.ElevatedButton(text='Получить картинку',
                                on_click= get_im_t,
                                disabled= True,
                                )
    
    peredelat_btn = ft.ElevatedButton(text='Удалить и сгенерировать новую',
                                on_click= get_im_t_peredel,
                                disabled= True,
                                visible= False,
                                bgcolor = ft.Colors.RED_ACCENT_400,
                                color = ft.Colors.BLACK
                                )

    panel_prmt = ft.Row(
            [
             change_theme_btn,
            ft.Column(
                [generated_im,
                 dscrpt_t,
                 user_prmt,
                 ft.Row(
                     [
                      get_btn_t,
                      peredelat_btn
                      ],
                      alignment=ft.MainAxisAlignment.CENTER
                      )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    #страница для 2d-3d
    

    def pick_file(e: ft.FilePickerResultEvent):
        if not e.files:
            selected_file.value = 'Ничего не выбрано'
        
        else:
            for el in e.files:
                dscrpt_im.value = f'Выбрана картинка: { (el.path).split('\\')[-1] }'
                selected_file.value = el.path

            get_btn_im.disabled = False

        page.update()

    dscrpt_im = ft.Text('')
   
    
    pick_dialog = ft.FilePicker(on_result= pick_file)
    page.overlay.append(pick_dialog)
    pick_file_btn = ft.ElevatedButton('Выберите картинку',
                                      icon= ft.Icons.UPLOAD_FILE,
                                      on_click= lambda _: pick_dialog.pick_files(allow_multiple= False))
    selected_file = ft.Text('')
    
    #имя 3д модели
    
    def name_cnt_t(e):
        st_n = 'слишком короткое имя' if len(model_name.value) < 1 else '' 
        model_name.counter_text = f'{st_n}'
        get_btn_im.disabled = False if len(model_name.value) > 0 else True
        
        page.update()


    model_name = ft.TextField(
        label= 'введите имя сгенерированной модели',
        width=400,
        value='awesome_mesh',
        on_change=name_cnt_t)


    ###

    def get_3d_im(e):
        get_btn_im.disabled = True
        page.navigation_bar.disabled = True
        pick_file_btn.disabled = True
        dscrpt_im.value = 'В процессе генерации...'
        page.update()
        
        
        try:
            
            generate_3d(selected_file.value)
            os.rename( os.path.abspath('./awesome_mesh.obj'), os.path.abspath(f'./3d_models/{model_name.value}.obj') )
            
            page.set_clipboard( os.path.abspath(f'./3d_models/{model_name.value}.obj') )
            dscrpt_im.value  = f'Готово, путь до 3д модели скопирован в буфер обмена!'

        except Exception as k:
            dscrpt_im.value  = f"""Произошла ошибка:
            {k}"""

        finally:

            get_btn_im.disabled = False
            page.navigation_bar.disabled = False
            pick_file_btn.disabled = False
            page.update()


    get_btn_im = ft.ElevatedButton(text='Получить 3D - модель',
                                on_click= get_3d_im,
                                disabled= True)
    
    ###

    panel_img = ft.Row(
            [
             change_theme_btn,
            ft.Column(
                [dscrpt_im,
                 model_name,
                 pick_file_btn,
                 get_btn_im
                    ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    
    ###

    md = """
## **При генерации картинки**

### * Напишите в конце "на белом фоне"
#####  _ Благодаря такому дополнению нейросеть понимает, что нужно сгенерировать 
##### только один объект. _
#
### * Если картинка своя, то лучше если объект выделяется
#####  _ То есть лучше будет если он не будет сливаться с фоном, так. _
#
#
## **При генерации 3д модели**
#
### * Качество 3д модели напрямую зависит от качества изображения
#####  _ Но есть **ограничение**: у картинки обрезается фон, и она преобразуется
#####  в разрешение 512 * 512,поэтому лучше будет, если картинка
##### не менее 512 * 512, и по этой же причине желательно, чтобы картинка была 
##### примерно 1024 * 1024, поскольку иначе нейросеть предобработает картинку и потеряет признаки! _
#
### * Если у вас ~8 Гб оперативной памяти, то закройте все другие приложения
##### _ Это хоть и немного, но увеличит ваши шансы на то, что приложение 
##### не закроется при генерации. _ 
#
"""

    tx_babushka = ft.Markdown(
            md,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            )

    panel_babushka = ft.Row(
            [
            tx_babushka
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    ###
    #навигация по страницам

    def navigate(e):
        index = page.navigation_bar.selected_index

        page.clean()

        if index == 0:
            dscrpt_t.value = ''
            page.add(panel_prmt)

        elif index == 1:
            dscrpt_im.value = ''
            page.add(panel_img)
        elif index == 2:
            page.add(panel_babushka)



    page.navigation_bar = ft.NavigationBar(
        destinations= [
            ft.NavigationBarDestination(
                icon= ft.Icons.TEXT_FIELDS_OUTLINED,
                label= "Из текста в картинку"
                ),
            ft.NavigationBarDestination(
                icon= ft.Icons.IMAGE,
                label= "Из картинки в 3D"
                ),
            ft.NavigationBarDestination(
                icon= ft.Icons.QUESTION_MARK,
                label= """Краткие рекомендации 
        для генерации"""
                )
            ],
        on_change= navigate
        )

    page.add(panel_prmt)

ft.app(main)