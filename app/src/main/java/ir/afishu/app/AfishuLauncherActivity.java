package ir.afishu.app;

import android.net.Uri;

import com.google.androidbrowserhelper.trusted.LauncherActivity;

import java.util.List;
import java.util.Set;

/**
 * Start every trusted AFISHU deep link in app navigation mode.
 *
 * The UI flag is visual only: it never grants access to a user or API.
 * Host validation prevents arbitrary external intent URLs being opened in the
 * trusted application's origin.
 */
public final class AfishuLauncherActivity extends LauncherActivity {
    private static final String TRUSTED_HOST = "afishu.ir";
    private static final Uri HOME = Uri.parse("https://afishu.ir/?afishu_app=1");

    @Override
    protected Uri getLaunchingUrl() {
        Uri requested = super.getLaunchingUrl();
        if (requested == null
                || !"https".equalsIgnoreCase(requested.getScheme())
                || !TRUSTED_HOST.equalsIgnoreCase(requested.getHost())) {
            return HOME;
        }

        Uri.Builder destination = requested.buildUpon().clearQuery();
        Set<String> names = requested.getQueryParameterNames();
        for (String name : names) {
            if ("afishu_app".equals(name)) {
                continue;
            }
            List<String> values = requested.getQueryParameters(name);
            for (String value : values) {
                destination.appendQueryParameter(name, value);
            }
        }
        destination.appendQueryParameter("afishu_app", "1");
        return destination.build();
    }
}
