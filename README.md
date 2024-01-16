## API файлового хранилища iMAS

### Version 1.

### GET:
1. *http(s)://domain-name.com/api/v1/files/*
> Обазятельные параметры:
> 1. user:
>    1. Type[int], Value[user] >= 0;
>    * Идентификатор пользователя файлы которого Вы хотите получить.

> Необязательные параметры (фильтры):
> 1. file_uuid:
>    1. Type[str], Value[uuid.uuid4()].
>    * Идентификатор файла. Идентификатор должен передан как строка состоящая из валидного типа uuid;
> 2. file_extension:
>    1. Type[str], Value[lookup for allowed file extensions in filemanager/conf.ini]
>    * Перед расширением файла необходимо поставить символ точки (.);
> 3. status:
>    1. Type[str], Value["R", "E", "P"].
>    * Статусы расшифровываются как ready, error, in progress соответственно;
> 4. service_name:
>    1. Type[str], Value[lookup for allowed service names in filemanager/conf.ini]
> 5. start:
>    1. Type[int], Value[Datetime | Date];
>    * Начальная дата поиска. Дата должна быть записана в формате: YYYY-MM-DD либо YYYY-MM-DD HH:MM:SS;
> 6. end:
>    1. Type[int], Value[Datetime | Date];
>    * Конечная дата поиска. Дата должна быть записана в формате: YYYY-MM-DD либо YYYY-MM-DD HH:MM:SS;
> 7. page:
>    1. Type[int], Value[page] >= 0;
>    2. Номер страницы.
> 8. page_size:
>    1. Type[int], Value[page_size] >= 0; 
>    * Количество записей для отображения на странице. Максимальное значение MaxPageSize устанавливается в filemanager/conf.ini.

