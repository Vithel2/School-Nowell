# Тестовая Android-сборка 0.1.0

`School-Nowell-debug.apk` — офлайн-приложение School's Nowell для Android 7.0+ в альбомной ориентации. Это debug-сборка, не публикация в Google Play. Нативная установка на физический телефон не проверялась.

Пакет собран Cordova 12 / cordova-android 13, SDK 34, JDK 17 и Gradle 8.7. Проверены подпись APK v2, целостность ZIP, Android manifest, соответствие SHA-256 исходного `Prototype.html`, наличие Cordova runtime и всех 46 медиафайлов. Подготовленный веб-пакет прошёл десять сюжетных маршрутов в Chromium.

Для проверки скачанного файла используйте сумму из `School-Nowell-debug.apk.sha256`. Для повторной сборки из корня репозитория: `bash scripts/setup-android.sh`, затем `npm run build:apk`.
