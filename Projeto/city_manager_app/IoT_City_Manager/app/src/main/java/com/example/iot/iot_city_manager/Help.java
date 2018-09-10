package com.example.iot.iot_city_manager;

import android.content.Intent;
import android.os.Bundle;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.MenuItem;
import android.view.View;

public class Help extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener {
    private DrawerLayout drawer;
    private ActionBarDrawerToggle toggle;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_help);

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        View decorView = getWindow().getDecorView();
        // Hide the status bar.
        int uiOptions = View.SYSTEM_UI_FLAG_VISIBLE;
        decorView.setSystemUiVisibility(uiOptions);


        drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        toggle = new ActionBarDrawerToggle(this, drawer,
                toolbar,
                R.string.navigation_drawer_open,
                R.string.navigation_drawer_close ) {
        };

        drawer.addDrawerListener(toggle);
        toggle.syncState();

    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();
        Intent intent;
        switch (id) {
            case R.id.nav_dashboard:
                intent = new Intent(this, MainActivity.class);
                startActivity(intent);
                break;
            case R.id.nav_map:
                intent = new Intent(this, MapsActivity.class);
                startActivity(intent);
                break;
            case R.id.temperature:
                intent = new Intent(this, Temperature.class);
                startActivity(intent);
                break;
            case R.id.noise:
                intent = new Intent(this, Noise.class);
                startActivity(intent);
                break;
            case R.id.lighting:
                intent = new Intent(this, Lighting.class);
                startActivity(intent);
                break;
            case R.id.radiation:
                intent = new Intent(this, UV_Radiation.class);
                startActivity(intent);
                break;
            case R.id.waste:
                intent = new Intent(this, Waste.class);
                startActivity(intent);
                break;
            case R.id.people:
                intent = new Intent(this, People.class);
                startActivity(intent);
                break;
            case R.id.alerts:
                intent = new Intent(this, AlertsActivity.class);
                startActivity(intent);
                break;
            case R.id.air:
                intent = new Intent(this, Air.class);
                startActivity(intent);
                break;
           default:
                break;
        }
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
}
