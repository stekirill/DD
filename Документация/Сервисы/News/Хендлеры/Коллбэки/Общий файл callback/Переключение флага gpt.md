## toggle_chatgpt

- **Назначение**: Переключение флага использования ChatGPT.
- **Действия**:
    - Проверяет подписку и состояние дайджеста, затем переключает флаг `chatgpt_flag`.
    - Обновляет медиафайл профиля пользователя.
    - Логирует событие и обновляет интерфейс с изображением.
- **Используемые компоненты**:
    - `update_image` для обновления изображения профиля.
    - `generate_settings_menu_keyboard` для обновления интерфейса.