package com.example.iot.iot_city;

import android.app.ProgressDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.FileProvider;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.webkit.MimeTypeMap;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;
import java.io.File;
import java.net.SocketTimeoutException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import static com.example.iot.iot_city.R.layout.activity_report2;

public class ReportActivity extends AppCompatActivity {
    private static final String TAG = "ReportActivity";
    static final int REQUEST_IMAGE_CAPTURE = 1;
    static final int REQUEST_VIDEO_CAPTURE = 2;
    private List<File> files = new ArrayList<>();
    private String sub_id;
    private ProgressDialog progress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(activity_report2);

        // Get sensor info that called report activity
        Bundle data = getIntent().getExtras();
        sub_id = data.getString("sub_id");

        // Check if we have write permissions
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.M){
            if(ActivityCompat.checkSelfPermission(this, android.Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED){
                requestPermissions(new String[] { android.Manifest.permission.READ_EXTERNAL_STORAGE}, 100);
                Log.d(TAG, "No write permission");
                return;
            }
        }
        // Enable camera buttons if we already have permission
        Log.d(TAG, "Permission granted, buttons enabled");
        enableButtons();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if(requestCode == 100 && (grantResults[0] == PackageManager.PERMISSION_GRANTED)) {
            // If we have permissions enable the camera buttons
            Log.d(TAG, "Permission granted, buttons enabled");
            enableButtons();
        } else {
            // If user does not grant permission go back to map
            Log.d(TAG, "No write permission, exiting report activity");
            finish();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            // Launch a toast informing the user that a photo was added
            Log.d(TAG, "One photo added successfully");
            Toast.makeText(ReportActivity.this, "One photo added successfully", Toast.LENGTH_SHORT).show();
        }
        else if (requestCode == REQUEST_VIDEO_CAPTURE && resultCode == RESULT_OK) {
            // Launch a toast informing the user that a video was added
            Log.d(TAG, "One video added successfully");
            Toast.makeText(ReportActivity.this, "One video added successfully", Toast.LENGTH_SHORT).show();
        }
    }

    private void enableButtons() {
        ImageView photo = (ImageView) findViewById(R.id.photo);
        ImageView camera = (ImageView) findViewById(R.id.camera);

        // photo onclick listener
        photo.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
                // Create file to save photo
                Log.d(TAG, "Creating new photo file");
                File cameraPhoto = createDirAndFile(getNewFileName("photo")+".jpg");
                Log.d(TAG, cameraPhoto.getAbsolutePath());
                // Add photo to file list to be sent with report
                Log.d(TAG, "File photo added to list");
                files.add(cameraPhoto);
                Uri pictureUri = FileProvider.getUriForFile(getApplicationContext(), getApplicationContext().getPackageName()+".provider", cameraPhoto);
                // Tell camera intent to save image to newly created file
                intent.putExtra(MediaStore.EXTRA_OUTPUT, pictureUri);
                startActivityForResult(intent, REQUEST_IMAGE_CAPTURE);
            }
        });

        // video onclick listener
        camera.setOnClickListener(new View.OnClickListener(){
            @Override
            public void onClick(View view){
                Intent intent = new Intent(MediaStore.ACTION_VIDEO_CAPTURE);
                // Create file to save video
                Log.d(TAG, "Creating new video file");
                File cameraVideo = createDirAndFile(getNewFileName("video")+".mp4");
                Log.d(TAG, cameraVideo.getAbsolutePath());
                // Add video to file list to be sent with report
                Log.d(TAG, "File video added to list");
                files.add(cameraVideo);
                Uri videoUri = FileProvider.getUriForFile(getApplicationContext(), getApplicationContext().getPackageName()+".provider", cameraVideo);
                // Limit video to 15 seconds
                intent.putExtra(MediaStore.EXTRA_DURATION_LIMIT, 15);
                // Tell camera intent to save video to newly created file
                intent.putExtra(MediaStore.EXTRA_OUTPUT, videoUri);
                startActivityForResult(intent, REQUEST_VIDEO_CAPTURE);
            }
        });
    }

    private File createDirAndFile(String fileName) {
        Log.d(TAG, "Creating new file");
        File filepath = Environment.getExternalStorageDirectory();
        // Create new dir for iot_city
        File iot_dir = new File(filepath.getAbsolutePath()+ "/IoTCity");
        Log.d(TAG, "IoT dir path: "+iot_dir.getAbsolutePath());
        // Check if directory exists
        if (!iot_dir.exists()) {
            Log.d(TAG, "Directory did not exists, creating new directory");
            iot_dir.mkdirs();
        }
        // Save file to iot dir
        return new File(iot_dir, fileName);
    }

    private String getNewFileName(String type) {
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        return "ReportIoT_"+ type + "_" + timeStamp;
    }

    private String getMimeType(String path) {
        // Get file type
        String extension = MimeTypeMap.getFileExtensionFromUrl(path);
        return MimeTypeMap.getSingleton().getMimeTypeFromExtension(extension);
    }

    public void sendReport(View view) {
        TextView tvsubject = (TextView) findViewById(R.id.subject);
        TextView tvinformation = (TextView) findViewById(R.id.information);
        TextView tvemail = (TextView) findViewById(R.id.email);
        TextView tvusername = (TextView) findViewById(R.id.username);

        // Create a progress dialog
        progress = new ProgressDialog(ReportActivity.this);
        progress.setTitle("Sending report");
        progress.setMessage("Please wait ...");

        // Get info for report and check if valid
        final String subject = tvsubject.getText().toString();
        if (subject.equals("")) {
            Toast.makeText(this, "Please enter a subject", Toast.LENGTH_SHORT).show();
            return;
        }
        final String information = tvinformation.getText().toString();
        if (information.equals("")) {
            Toast.makeText(this, "Please enter some information", Toast.LENGTH_SHORT).show();
            return;
        }
        final String username = tvusername.getText().toString();
        if (username.equals("")) {
            Toast.makeText(this, "Please enter your name", Toast.LENGTH_SHORT).show();
            return;
        }
        final String email = tvemail.getText().toString();
        if (email.equals("")) {
            Toast.makeText(this, "Please enter your email", Toast.LENGTH_SHORT).show();
            return;
        }

        // Start progress dialog
        progress.show();

        // Thread to send post request
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {
                OkHttpClient client = new OkHttpClient();

                // Add the report information to the post body
                MultipartBody.Builder builder = new MultipartBody.Builder()
                        .setType(MultipartBody.FORM)
                        .addFormDataPart("title", subject)
                        .addFormDataPart("information", information)
                        .addFormDataPart("username", username)
                        .addFormDataPart("email", email)
                        .addFormDataPart("subscription", sub_id);

                // For each file add to post body
                for(File f : files) {
                    if(f.exists()) {
                        String content_type = getMimeType(f.getPath());
                        Log.d(TAG, content_type);
                        String file_path = f.getAbsolutePath();
                        builder.addFormDataPart("files", file_path.substring(file_path.lastIndexOf("/")+1), RequestBody.create(MediaType.parse(content_type), f));
                    }
                }

                RequestBody request_body = builder.build();

                Request request = new Request.Builder()
                        .url("http://178.62.255.129/mobile/report")
                        .post(request_body)
                        .build();

                try {
                    // Execute the post request
                    Response response = client.newCall(request).execute();
                    // Stop progress dialog
                    progress.dismiss();
                    // Close connection
                    response.close();
                    // Finish report activity
                    finish();
                } catch (SocketTimeoutException e) {
                    e.printStackTrace();
                    // Stop the progress dialog
                    progress.dismiss();
                    // Launch a toast informing the user of the error
                    ReportActivity.this.runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(ReportActivity.this, "Could not contact server", Toast.LENGTH_LONG).show();
                        }
                    });
                    Log.d(TAG, "Could not contact server");
                    // Remove files from user storage if report not successful
                    Log.d(TAG, "Deleting files");
                    for(File f : files)
                        f.delete();
                    // Finish report activity
                    finish();
                } catch (Exception e) {
                    e.printStackTrace();
                    // Stop the progress dialog
                    progress.dismiss();
                    // Launch a toast informing the user of the error
                    ReportActivity.this.runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(ReportActivity.this, "Could not send report", Toast.LENGTH_LONG).show();
                        }
                    });
                    Log.d(TAG, "Could not send report");
                    // Remove files from user storage if report not successful
                    Log.d(TAG, "Deleting files");
                    for(File f : files)
                        f.delete();
                    // Finish report activity
                    finish();
                }
            }
        });
        // Start the thread
        t.start();
    }
}