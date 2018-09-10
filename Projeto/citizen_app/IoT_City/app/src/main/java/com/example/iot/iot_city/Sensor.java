package com.example.iot.iot_city;

import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;

public class Sensor {
    private String name, type;
    private String sub_name;
    private String sub_id;
    private String id;
    private LatLng loc;
    private Marker marker;

    public Sensor(String name, String sub_name, String sub_id, String type, LatLng loc, String id){
        this.name = name;
        this.sub_name = sub_name;
        this.sub_id = sub_id;
        this.type = type;
        this.loc = loc;
        this.id = id;
    }
    public String getName() { return name; }
    public String getType() { return type; }
    public String getSubName() { return sub_name; }
    public String getSubId() { return sub_id; }
    public LatLng getLatLng() { return loc; }
    public Marker getMarker() { return marker; }
    public void setMarker(Marker m) { this.marker = m; }
    public String getId(){
        return this.id;
    }
}