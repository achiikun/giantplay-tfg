package cat.uab.giantplayadmin;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Point;
import android.hardware.Camera;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.os.Vibrator;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Display;
import android.view.MotionEvent;
import android.view.View;
import android.view.Window;
import android.widget.ImageView;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import cat.uab.giantplayadmin.model.GPParams;
import cat.uab.giantplayadmin.model.GPUser;
import cat.uab.giantplayadmin.util.ConnectionManager;

public class PlayActivity extends AppCompatActivity implements SensorEventListener, View.OnTouchListener {

    public GPUser user;
    private ImageView imageView;

    private SensorManager manager;
    private Sensor orientationSensor;

    private ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();

    private boolean paused;

    private volatile boolean moveAwaiting = false, moveAwaiting2 = false;
    private volatile int moveX, moveY, moveX2, moveY2;

    private volatile float[] rotationVector;
    private float[] oldRotationVector;

    private long eventTimeLapse = 1000/GPParams.FPS;
    private Vibrator vibrator;

    private Camera camera;
    private Camera.Parameters cameraParameters;
    private Bitmap bitmap;
    private Canvas canvas;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        MainActivity.playActivity = this;

        requestWindowFeature(Window.FEATURE_NO_TITLE);

        toggleHideyBar();

        //if (Build.VERSION.SDK_INT < 16) {
        //    getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
        //            WindowManager.LayoutParams.FLAG_FULLSCREEN);
        /*}
        else {
            View decorView = getWindow().getDecorView();
            // Hide Status Bar.
            int uiOptions = View.SYSTEM_UI_FLAG_FULLSCREEN;
            decorView.setSystemUiVisibility(uiOptions);
        }*/

        setContentView(R.layout.activity_play);

        String key = getIntent().getStringExtra("userkey");

        this.user = ConnectionManager.getInstance().getUser(key);

        if(this.user == null)
            finish();

        manager = (SensorManager) this.getApplicationContext()
                .getSystemService(Context.SENSOR_SERVICE);

        orientationSensor = manager.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR);

        vibrator = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);

        PackageManager pm = getPackageManager();

        if (pm.hasSystemFeature(PackageManager.FEATURE_CAMERA_FLASH) && ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                == PackageManager.PERMISSION_GRANTED) {
            camera = Camera.open();
            if( camera.getParameters().getSupportedFlashModes().contains(Camera.Parameters.FLASH_MODE_TORCH)){
                cameraParameters = camera.getParameters();
            }
        }

        Display display = getWindowManager().getDefaultDisplay();
        Point size = new Point();
        display.getSize(size);

        bitmap = Bitmap.createBitmap(size.x, size.y, Bitmap.Config.RGB_565);
        canvas = new Canvas(bitmap);
        canvas.drawRGB(255,255,255);
        canvas.save();

        imageView = findViewById(R.id.imageView);
        imageView.setImageBitmap(bitmap);
        imageView.setScaleType(ImageView.ScaleType.FIT_XY);
        imageView.setOnTouchListener(this);


        scheduler.submit(runSend);

    }

    Runnable runSend = new Runnable() {
        @Override
        public void run() {

            if(!paused){
                if(moveAwaiting){
                    ConnectionManager.getInstance().sendEvent(user, "tmove", moveX, moveY);
                    moveAwaiting = false;
                }

                if(moveAwaiting2){
                    ConnectionManager.getInstance().sendEvent(user, "tpmove", moveX2, moveY2);
                    moveAwaiting2 = false;
                }

                if(rotationVector != null) {

                    if(oldRotationVector != null){
                        if(oldRotationVector == rotationVector)
                            Log.d("rotationVector", "NO");
                        else
                            Log.d("rotationVector", "YEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES");
                        oldRotationVector = rotationVector;
                    }

                    ConnectionManager.getInstance().sendEvent(user, "rotvec",
                            rotationVector[0],
                            rotationVector[1],
                            rotationVector[2],
                            rotationVector[3]
                    );
                }

            }
            if(!scheduler.isShutdown())
                scheduler.schedule(runSend, eventTimeLapse, TimeUnit.MILLISECONDS);

        }
    };

    @Override
    public boolean onTouch(View view, MotionEvent motionEvent) {
        String event = null;
        String event2 = null;

        float x = motionEvent.getX();
        float y = motionEvent.getY();

        float x2 = motionEvent.getX();
        float y2 = motionEvent.getY();

        int action = motionEvent.getAction();
        int actionMasked = motionEvent.getActionMasked();
        Log.i("PlayActivity", "onTouch: " + action + " " + actionMasked);
        int pointerCount = motionEvent.getPointerCount();

        switch (action) {
            case MotionEvent.ACTION_DOWN:
                event = "tdown";
                break;
            case MotionEvent.ACTION_MOVE:
                for(int i = 0; i < pointerCount; ++i)
                {
                    int pointerIndex = i;
                    int pointerId = motionEvent.getPointerId(pointerIndex);
                    if(pointerId == 0)
                    {
                        event = "tmove";
                        x = motionEvent.getX(pointerIndex);
                        y = motionEvent.getY(pointerIndex);
                    }
                    if(pointerId == 1)
                    {
                        event2 = "tpmove";
                        x2 = motionEvent.getX(pointerIndex);
                        y2 = motionEvent.getY(pointerIndex);
                    }
                }
                break;
            case MotionEvent.ACTION_UP:
                event = "tup";
                break;
            case MotionEvent.ACTION_CANCEL:
                break;
            default:
                break;
        }

        switch(actionMasked){
            case MotionEvent.ACTION_POINTER_DOWN:

                for(int i = 0; i < pointerCount; ++i)
                {
                    int pointerIndex = i;
                    int pointerId = motionEvent.getPointerId(pointerIndex);

                    if(pointerId == 1)
                    {
                        event = "tpdown";
                        x = motionEvent.getX(pointerIndex);
                        y = motionEvent.getY(pointerIndex);
                    }
                }

                break;
            case MotionEvent.ACTION_POINTER_UP:

                for(int i = 0; i < pointerCount; ++i)
                {
                    int pointerIndex = i;
                    int pointerId = motionEvent.getPointerId(pointerIndex);

                    if(pointerId == 1)
                    {
                        event = "tpup";
                        x = motionEvent.getX(pointerIndex);
                        y = motionEvent.getY(pointerIndex);
                    }
                }

                break;
            default:
                break;
        }

        if(event != null) {
            if ("tdown".equals(event)) {
                ConnectionManager.getInstance().sendEvent(user, event, x, y);
            } else if ("tup".equals(event)) {
                moveAwaiting = false;
                ConnectionManager.getInstance().sendEvent(user, event, x, y);
            } else if ("tpdown".equals(event)) {
                ConnectionManager.getInstance().sendEvent(user, event, x, y);
            } else if ("tpup".equals(event)) {
                moveAwaiting2 = false;
                ConnectionManager.getInstance().sendEvent(user, event, x, y);
            } else if ("tmove".equals(event)) {
                moveX = (int) x;
                moveY = (int) y;
                moveAwaiting = true;
            }
        }

        if(event2 != null) {
            if ("tpmove".equals(event)) {
                moveX2 = (int) x2;
                moveY2 = (int) y2;
                moveAwaiting2 = true;
            }
        }

        return true;
    }

    public void toggleHideyBar() {

        int uiOptions = getWindow().getDecorView().getSystemUiVisibility();
        int newUiOptions = uiOptions;
        boolean isImmersiveModeEnabled =
                ((uiOptions | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY) == uiOptions);

        if (isImmersiveModeEnabled) {
            Log.i("Play", "Turning immersive mode mode off. ");
        } else {
            Log.i("Play", "Turning immersive mode mode on.");
        }

        // Navigation bar hiding:  Backwards compatible to ICS.
        if (Build.VERSION.SDK_INT >= 14) {
            newUiOptions ^= View.SYSTEM_UI_FLAG_HIDE_NAVIGATION;
        }

        // Status bar hiding: Backwards compatible to Jellybean
        if (Build.VERSION.SDK_INT >= 16) {
            newUiOptions ^= View.SYSTEM_UI_FLAG_FULLSCREEN;
        }

        if (Build.VERSION.SDK_INT >= 18) {
            newUiOptions ^= View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY;
        }

        getWindow().getDecorView().setSystemUiVisibility(newUiOptions);
        //END_INCLUDE (set_ui_flags)
    }

    @Override
    protected void onPause() {
        super.onPause();
        paused = true;
        manager.unregisterListener(this);
    }

    @Override
    protected void onResume() {
        manager.registerListener(this, orientationSensor, SensorManager.SENSOR_DELAY_UI);
        paused = false;
        super.onResume();
    }

    @Override
    protected void onDestroy() {
        MainActivity.playActivity = null;
        scheduler.shutdownNow();
        super.onDestroy();
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        if (sensorEvent.sensor.getType() == Sensor.TYPE_ROTATION_VECTOR) {

            rotationVector = sensorEvent.values;
            //ConnectionManager.getInstance().sendEvent(user, "rotvec", sensorEvent.values);
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }

    private void reset() {
        if (vibrator != null && vibrator.hasVibrator()) {
            try {
                vibrator.cancel();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        if (camera != null) {
            try {
                cameraParameters.setFlashMode(Camera.Parameters.FLASH_MODE_OFF);
                camera.setParameters(cameraParameters);
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        rgb(new float[]{255,255,255});
    }

    public void rumble(float[] values){
        System.out.print("RUMBLE");
        if(vibrator != null && vibrator.hasVibrator()){

            long[] l = new long[values.length];
            for (int i = 0; i < values.length; i++) {
                l[i] = (long) values[i];
            }

            try{
                vibrator.vibrate(l, -1);
            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }

    private void light(float[] values) {
        if(camera != null){
            try {

                boolean on = values[0] != 0;
                if (!on) {

                    cameraParameters = camera.getParameters();
                    camera.stopPreview();
                    cameraParameters.setFlashMode(Camera.Parameters.FLASH_MODE_OFF);
                    camera.setParameters(cameraParameters);
                    cameraParameters.setFlashMode(Camera.Parameters.FLASH_MODE_OFF);
                    camera.setParameters(cameraParameters);
                    camera.stopPreview();

                } else {

                    cameraParameters = camera.getParameters();
                    camera.stopPreview();
                    cameraParameters.setFlashMode(Camera.Parameters.FLASH_MODE_OFF);
                    camera.setParameters(cameraParameters);
                    cameraParameters.setFlashMode(Camera.Parameters.FLASH_MODE_TORCH);
                    camera.setParameters(cameraParameters);
                    camera.startPreview();
                }

            }catch (Exception e){
                e.printStackTrace();
            }
        }
    }

    private void rgb(float[] values) {

        int r = (int) values[0];
        int g = (int) values[1];
        int b = (int) values[2];

        canvas.drawRGB(r,g,b);
        canvas.save();

        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                imageView.setImageBitmap(bitmap);
            }
        });

    }


    public void onEvent(String eventKey, float[] values) {

        switch (eventKey){
            case "rst":
                reset();
                break;
            case "rmbl":
                rumble(values);
                break;
            case "light":
                light(values);
                break;
            case "rgb":
                rgb(values);
                break;
        }

    }


}
