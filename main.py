import yadisk
import os


def download_all_files_from_folder(yandex_disk_folder, save_folder):
    y = yadisk.YaDisk(token='y0_AgAEA7qj-qbFAAp4SgAAAADsTMC1KDDnuQpYREyJJczUd61LFjWErLI')

    try:
        items = y.listdir(yandex_disk_folder)
        for item in items:
            if item.is_file():
                file_name = item.name
                save_path = os.path.join(save_folder, file_name)

                # Проверяем, существует ли файл с таким же именем в целевой папке
                if not os.path.exists(save_path):
                    y.download(item.path, save_path)
                    print(f'Файл "{file_name}" успешно скачан и сохранен в {save_path}')
                else:
                    print(f'Файл "{file_name}" уже существует в целевой папке, пропускаем его.')

    except Exception as e:
        print(f'Ошибка при скачивании файлов: {str(e)}')

# Пример использования функции
yandex_disk_folder = '/media'
save_folder = 'media/'
download_all_files_from_folder(yandex_disk_folder, save_folder)