# AFISHU Android — Trusted Web Activity

پروژه اندروید اختصاصی آفیش‌یو با `applicationId=ir.afishu.app` و بر پایهٔ Chromium Trusted Web Activity.

پیش‌نیاز سرویس GitHub Actions: Java 17، Android SDK API 36، Gradle 8.11.1 و Android Gradle Plugin 8.10.1. این موارد توسط `.github/workflows/android.yml` به‌صورت خودکار نصب می‌شوند.

برای ساخت بدون کامپیوتر، فایل‌های همین پوشه را در ریشهٔ Repository خصوصی GitHub قرار دهید، سپس در تب Actions گزینه **Build AFISHU Android → Run workflow** را انتخاب کنید. Artifact **AFISHU-Android-debug-APK** خروجی نصب روی گوشی است.

ورژن Release فقط زمانی ایجاد می‌شود که چهار Secret امضای دائمی تنظیم شده باشند؛ جزئیات دقیق در `../deployment/DEPLOYMENT_FA.md` بستهٔ کامل آمده است. فایل `assetlinks-*.json` هم‌زمان با هر APK ساخته می‌شود و برای حذف نوار مرورگر باید با نام `assetlinks.json` در ریشهٔ دامنه و پوشهٔ `.well-known` قرار بگیرد.

هیچ‌گونه رمز، API key، کلید خصوصی یا دسترسی مدیریتی وردپرس در کد وجود ندارد.

## اصلاح سازگاری API 36 — نسخه 1.0.1

این نسخه، مشکل شناخته‌شده ناسازگاری AAR Metadata وابستگی‌های Android Browser Helper 2.7.3 با `compileSdk 35` را با ارتقای هماهنگ `compileSdk` به 36، AGP به 8.10.1 و نصب Android SDK 36 در GitHub Actions برطرف می‌کند. `targetSdk 35` و `minSdk 24` عمداً ثابت مانده‌اند تا تغییرات رفتار Runtime ناخواسته ایجاد نشود.

**برای مخزن از پیش ساخته‌شده:** فقط فایل‌های `app/build.gradle` و `build.gradle` و `.github/workflows/android.yml` را در همان مسیرهای ریشهٔ Repository با نسخه جدید جایگزین و Commit کنید. ساخت APK در تب Actions به‌صورت خودکار شروع می‌شود. نسخهٔ APK باید بعد از اجرای موفق Workflow تأیید شود؛ بررسی‌های استاتیک جایگزین Gradle Build واقعی نیستند.
