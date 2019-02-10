package cat.uab.giantplayadmin.util;

import android.graphics.Point;

import org.json.JSONObject;

import cat.uab.giantplayadmin.model.GPUser;

public interface ConnectionManagerListener extends ConnectTastListener {

    Point getWindowSize();

    void onConnect();
    void onDisconnect();

    void onLogin(GPUser user);
    void onLogout(GPUser user);

    void onAdmin(JSONObject admin);
    void onEvent(GPUser user, String eventKey, float[] values);

    void sendEvent(GPUser user, String event, double[] values);
    void sendEvent(GPUser user, String event, float[] values);

}
