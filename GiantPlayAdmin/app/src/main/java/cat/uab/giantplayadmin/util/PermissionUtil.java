package cat.uab.giantplayadmin.util;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;

public class PermissionUtil {

    public static final int MY_PERMISSIONS_REQUEST = 300;

    private static final PermissionUtil ourInstance = new PermissionUtil();
    private PermissionListener listener;

    public static PermissionUtil getInstance() {
        return ourInstance;
    }

    private PermissionUtil() {
    }

    public void setListener(PermissionListener listener){
        this.listener = listener;
    }

    public void checkPermission(Activity context) {
        // Here, thisActivity is the current activity
        if (ContextCompat.checkSelfPermission(context,
                Manifest.permission.INTERNET)
                != PackageManager.PERMISSION_GRANTED ||
                ContextCompat.checkSelfPermission(context,
                Manifest.permission.ACCESS_WIFI_STATE)
                != PackageManager.PERMISSION_GRANTED) {

                // No explanation needed; request the permission
                ActivityCompat.requestPermissions(context,
                        new String[]{Manifest.permission.INTERNET, Manifest.permission.ACCESS_WIFI_STATE},
                        MY_PERMISSIONS_REQUEST);

                // MY_PERMISSIONS_REQUEST_READ_CONTACTS is an
                // app-defined int constant. The callback method gets the
                // result of the request.

        } else {
            // Permission has already been granted
            listener.permissionGranted();
        }
    }


    public void onRequestPermissionResult(int requestCode, String[] permissions, int[] grantResults) {

        switch (requestCode) {
            case PermissionUtil.MY_PERMISSIONS_REQUEST: {

                // If request is cancelled, the result arrays are empty.
                if (grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED
                        && grantResults[1] == PackageManager.PERMISSION_GRANTED) {
                    // permission was granted, yay! Do the
                    // contacts-related task you need to do.
                    listener.permissionGranted();
                } else {
                    // permission denied, boo! Disable the
                    // functionality that depends on this permission.
                    listener.permissionNotGranted();
                }
                return;
            }

            // other 'case' lines to check for other
            // permissions this app might request.
        }



    }
}
