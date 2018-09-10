package com.example.iot.iot_city;

import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Geocoder;
import android.location.Location;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.View;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import com.google.android.gms.maps.CameraUpdate;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.BitmapDescriptor;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class MapSensor extends AppCompatActivity implements OnMapReadyCallback, GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener, LocationListener {
    private static final String TAG = "MapsActivity";
    private GoogleApiClient mGoogleApiClient;
    private LocationRequest locationRequest;
    private Location mCurrentLocation;
    private boolean listeningToChanges = false;
    private GoogleMap mMap;
    private Marker myself;
    private List<Sensor> sensors = new ArrayList<>();
    private CheckBox tempbox;
    private CheckBox lightbox;
    private CheckBox noisebox;
    private CheckBox uvbox;
    private CheckBox airbox;
    private CheckBox peoplebox;
    private CheckBox wastebox;
    private String calling_id = "";
    private LatLng sensor_loc = new LatLng(0,0);

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);

        // map
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager().findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

        // gps
        mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addApi(LocationServices.API)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .build();


        // Setting gps time intervals
        locationRequest = new LocationRequest();
        locationRequest.setInterval(10000);
        locationRequest.setFastestInterval(5000);
        locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);

        // checkboxes
        tempbox = (CheckBox) findViewById(R.id.checkBoxTemp);
        lightbox = (CheckBox) findViewById(R.id.checkBoxLight);
        noisebox = (CheckBox) findViewById(R.id.checkBoxNoise);
        uvbox = (CheckBox) findViewById(R.id.checkBoxUV);
        airbox = (CheckBox) findViewById(R.id.checkBoxAir);
        peoplebox = (CheckBox) findViewById(R.id.checkBoxPeople);
        wastebox = (CheckBox) findViewById(R.id.checkBoxWaste);
    }

    @Override
    protected void onStart() {
        super.onStart();
        // Connect gps on start
        mGoogleApiClient.connect();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Start listening to changes on resume
        if(mGoogleApiClient.isConnected() && !listeningToChanges) {
            Log.d(TAG, "Requesting updates on resume");
            requestLocationUpdates();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        // Stop listening to changes on pause
        if (mGoogleApiClient.isConnected() && listeningToChanges) {
            stopLocationUpdates();
            Log.d(TAG, "Stopped listening to changes on pause");
        }
    }

    @Override
    protected void onStop() {
        super.onStop();
        // Disconnect gps on stop
        mGoogleApiClient.disconnect();
        Log.d(TAG, "GPS disconnected");
    }

    // Map methods
    @Override
    public void onMapReady(GoogleMap googleMap) {

        mMap = googleMap;
        mMap.getUiSettings().setMyLocationButtonEnabled(true);

        Bundle data = getIntent().getExtras();
        calling_id = data.getString("Sensor_id");


        if(mMap != null){
            mMap.setInfoWindowAdapter(new GoogleMap.InfoWindowAdapter(){
                @Override
                public View getInfoWindow(Marker marker){
                    return null;
                }

                @Override
                public View getInfoContents(Marker marker) {
                    View v = getLayoutInflater().inflate(R.layout.info_window, null);
                    TextView txt1 = (TextView) v.findViewById(R.id.txt1);
                    TextView txt2 = (TextView) v.findViewById(R.id.txt2);

                    // Fill marker info window
                    if(marker.getTitle().equals(getResources().getString(R.string.you_are_here))) {
                        return null;
                    } else {
                        txt1.setText(marker.getTitle());
                        txt2.setText(marker.getSnippet());
                    }
                    return v;
                }
            });

            mMap.setOnInfoWindowClickListener(new GoogleMap.OnInfoWindowClickListener() {
                @Override
                public void onInfoWindowClick(Marker marker) {
                    if(marker.getTitle().equals(getResources().getString(R.string.you_are_here)))
                        return;
                    // Pass marker subscription id to report activity
                    Bundle data = new Bundle();
                    for(Sensor s : sensors) {
                        if(s.getMarker().equals(marker))    {
                            data.putString("sub_id", s.getSubId());
                        }
                    }
                    // If marker info window is clicked start report activity
                    Intent intent = new Intent(getBaseContext(), ReportActivity.class);
                    intent.putExtras(data);
                    intent.putExtras(data);
                    startActivity(intent);
                }
            });


        }
        mMap.moveCamera(CameraUpdateFactory.newLatLng(sensor_loc));
        mMap.animateCamera(CameraUpdateFactory.zoomTo(13));

        // Set zoom preferences
        mMap.setMinZoomPreference(10);
        mMap.setMaxZoomPreference(20);
    }

    @Override
    public void onConnected(@Nullable Bundle bundle) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                Log.d(TAG, "No GPS permission");
                requestPermissions(new String[] {
                        android.Manifest.permission.ACCESS_FINE_LOCATION
                }, 10);
                return;
            }
        }
        // If there is no previous location fetch last known one
        if (mCurrentLocation == null) {
            Log.d(TAG, "No previous location");
            mCurrentLocation = LocationServices.FusedLocationApi.getLastLocation(mGoogleApiClient);
            if(mCurrentLocation != null) Log.d(TAG, mCurrentLocation.toString());
        }
        // Start listening to location changes if not doing so already
        if(!listeningToChanges) {
            Log.d(TAG, "Started listening to location changes");
            requestLocationUpdates();
        }
        // Launch async task (populating map) if we have a location and center the map on user location
        if(mCurrentLocation != null) {
            myself = mMap.addMarker(new MarkerOptions().position(new LatLng(mCurrentLocation.getLatitude(), mCurrentLocation.getLongitude())));
            myself.setTitle(getResources().getString(R.string.you_are_here));
            mMap.moveCamera(CameraUpdateFactory.newLatLng(new LatLng(mCurrentLocation.getLatitude(), mCurrentLocation.getLongitude())));
            mMap.animateCamera(CameraUpdateFactory.zoomTo(13));
            new Sensors().execute();
            Log.d(TAG, "Centered map on user location");
        }
    }

    @Override
    public void onConnectionSuspended(int i) {

    }

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {

    }

    @Override
    public void onLocationChanged(Location location) {
        mCurrentLocation = location;
        Log.d(TAG, "New lat "+location.getLatitude() +" lon " + location.getLongitude());
        Log.d(TAG, "Location changed, launching new async task");
        // Update user location
        mMap.moveCamera(CameraUpdateFactory.newLatLng(new LatLng(mCurrentLocation.getLatitude(), mCurrentLocation.getLongitude())));
        if(myself != null)
            myself.remove();
        myself = mMap.addMarker(new MarkerOptions().position(new LatLng(mCurrentLocation.getLatitude(), mCurrentLocation.getLongitude())));
        myself.setTitle(getResources().getString(R.string.you_are_here));

        // Remove previous markers
        for(int i = 0; i < sensors.size(); i++) {
            Sensor tmp = sensors.get(i);
            tmp.getMarker().remove();
        }
        // Clear sensors list
        sensors.clear();
        // When location changes fetch new data
        new Sensors().execute();
    }

    public void geoLocate(View view) throws IOException {
        EditText et = (EditText) findViewById(R.id.editText3);
        String location = et.getText().toString();
        // Check user input
        if(location.equals("")) {
            Toast.makeText(this, "Please enter a valid location", Toast.LENGTH_LONG).show();
            Log.d(TAG, "Invalid location to locate");
            return;
        }

        Geocoder gc = new Geocoder(this);
        android.location.Address address = gc.getFromLocationName(location, 1).get(0);

        double lat = address.getLatitude();
        double lng = address.getLongitude();

        LatLng ll = new LatLng(lat, lng);
        CameraUpdate update = CameraUpdateFactory.newLatLngZoom(ll, 13);

        // Set camera on new location
        mMap.moveCamera(update);
        // Clear text box
        et.setText("");
    }

    public void resetLocation(View view) {
        // Reset location to where the user is
        if(myself != null) {
            mMap.moveCamera(CameraUpdateFactory.newLatLng(myself.getPosition()));
            mMap.animateCamera(CameraUpdateFactory.zoomTo(13));
        }
        Log.d(TAG, "Location reset");
    }

    private void requestLocationUpdates() {
        // Start listening to location changes
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            Intent intent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
            startActivity(intent);
            return;
        }
        LocationServices.FusedLocationApi.requestLocationUpdates(mGoogleApiClient, locationRequest, this);
        listeningToChanges = true;
    }

    private void stopLocationUpdates() {
        // Stop listening to location changes
        LocationServices.FusedLocationApi.removeLocationUpdates(mGoogleApiClient, this);
        listeningToChanges = false;
    }

    public void onCheckboxClicked(View view) {
        // Is the view now checked?
        boolean checked = ((CheckBox) view).isChecked();    //True for checked, false for unchecked
        // Check which checkbox was clicked
        switch(view.getId()) {
            //If clicked in lighting checkbox
            case R.id.checkBoxLight:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("IL"))      //If it is a lighting sensor
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("IL"))      //If it is a lighting sensor
                            sensor.getMarker().setVisible(false);
                    }
                }
                break;
            //If clicked in temperature checkbox
            case R.id.checkBoxTemp:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("TE"))      //If it is a temperature sensor
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("TE"))      //If it is a temperature sensor
                            sensor.getMarker().setVisible(false);    //Make the marker invisible in the map
                    }
                }
                break;
            //If clicked in noise checkbox
            case R.id.checkBoxNoise:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("SO"))      //If it is a noise sensor
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("SO"))      //If it is a noise sensor
                            sensor.getMarker().setVisible(false);    //Make the marker invisible in the map
                    }
                }
                break;
            //If clicked in UV radiation checkbox
            case R.id.checkBoxUV:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("RA"))      //If it is a UV radiation sensor
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("RA"))      //If it is a UV radiation sensor
                            sensor.getMarker().setVisible(false);    //Make the marker invisible in the map
                    }
                }
                break;
            //If clicked in air checkbox
            case R.id.checkBoxAir:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("AI"))      //If it is a air sensor
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("AI"))      //If it is a air sensor
                            sensor.getMarker().setVisible(false);    //Make the marker invisible in the map
                    }
                }
                break;
            //If clicked in waste checkbox
            case R.id.checkBoxWaste:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("WA"))      //If it is a waste sensor
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("WA"))      //If it is a waste sensor
                            sensor.getMarker().setVisible(false);    //Make the marker invisible in the map
                    }
                }
                break;
            //If clicked in people checkbox
            case R.id.checkBoxPeople:
                if (checked){   //If it is checked
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("PE"))      //If it is a people counter
                            sensor.getMarker().setVisible(true);    //Make the marker visible in the map
                    }
                } else {
                    for (Sensor sensor : sensors) { //Iterate through the list of sensors
                        if (sensor.getType().equals("PE"))      //If it is a people counter
                            sensor.getMarker().setVisible(false);    //Make the marker invisible in the map
                    }
                }
                break;
        }
    }

    // Async task populate map
    private class Sensors extends AsyncTask<Void, Void, Void> {
        private JSONObject json_response = null;
        private String url = "http://178.62.255.129/mobile/map/";

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
        }
        @Override
        protected Void doInBackground(Void... params) {
            // Get map data
            try {
                URL url = new URL(this.url);
                HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
                httpURLConnection.setConnectTimeout(5000);
                InputStream input = httpURLConnection.getInputStream();
                BufferedReader reader = new BufferedReader(new InputStreamReader(input));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    sb.append(line);
                }
                json_response = new JSONObject(sb.toString());
                reader.close();
                input.close();
                httpURLConnection.disconnect();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return null;
        }
        @Override
        protected void onPostExecute(Void avoid) {
            // If no response
            if (json_response == null) {
                Log.d(TAG, "No response found");
            } else {
                try {
                    JSONArray jsensors = json_response.getJSONArray("sensors");
                    for(int i=0; i < jsensors.length(); i++) {
                        JSONObject jsensor = jsensors.getJSONObject(i);
                        String sub_name = jsensor.getString("sub_name");
                        String id = jsensor.getString("id");
                        String snippet = sub_name + " last value: ";
                        LatLng loc = new LatLng(jsensor.getDouble("lat"), jsensor.getDouble("lon"));
                        String title = jsensor.getString("name");
                        String type = jsensor.getString("type");
                        String sub_id = jsensor.getString("sub_id");
                        BitmapDescriptor icon = null;
                        switch (type) {
                            case "IL":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.technology);
                                snippet += jsensor.getString("sub_value") + " %";
                                break;
                            case "WA":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.bin3);
                                snippet += jsensor.getString("sub_value") + " %";
                                break;
                            case "RA":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.summer);
                                snippet += jsensor.getString("sub_value") + " UV";
                                break;
                            case "TE":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.cold);
                                snippet += jsensor.getString("sub_value") + " ºC";
                                break;
                            case "SO":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.multimedia2);
                                snippet += jsensor.getString("sub_value") + " dB";
                                break;
                            case "AI":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.air);
                                snippet += jsensor.getString("sub_value");
                                break;
                            case "PE":
                                icon = BitmapDescriptorFactory.fromResource(R.mipmap.people2);
                                snippet += jsensor.getString("sub_value") + " %";
                                break;
                        }

                        Marker tmp = mMap.addMarker(new MarkerOptions().position(loc).title(title).snippet(snippet).icon(icon));
                        Sensor tmp_sensor = new Sensor(title, sub_name, sub_id, type, loc, id);
                        tmp_sensor.setMarker(tmp);
                        sensors.add(tmp_sensor);
                        //System.out.println(tmp_sensor.getId());
                        if(tmp_sensor.getId().equals(calling_id)){
                            sensor_loc = tmp_sensor.getLatLng();
                            System.out.println("got it");
                            tmp.showInfoWindow();
                        }

                    }
                    for(Sensor s : sensors) {
                        switch(s.getType()) {
                            case "IL":
                                if(!lightbox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                            case "WA":
                                if(!wastebox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                            case "RA":
                                if(!uvbox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                            case "TE":
                                if(!tempbox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                            case "SO":
                                if(!noisebox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                            case "AI":
                                if(!airbox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                            case "PE":
                                if(!peoplebox.isChecked())
                                    s.getMarker().setVisible(false);
                                break;
                        }
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
