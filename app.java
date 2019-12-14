package com.example.bajwa_000.bluetooth;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Intent;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Set;

public class MainActivity extends AppCompatActivity {

    BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    ListView listv;
    ArrayList list2 = new ArrayList();
    Set<BluetoothDevice> pairedDevices = mBluetoothAdapter.getBondedDevices();



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    //////start////////////////////

        if (!mBluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivity(enableBtIntent);
        }
        if (mBluetoothAdapter.isEnabled()) {



            if (pairedDevices.size() > 0) {
                listv= findViewById(R.id.text1);
                // There are paired devices. Get the name and address of each paired device.
                for (BluetoothDevice device : pairedDevices) {

                    String deviceName = device.getName();
                    String deviceHardwareAddress = device.getAddress(); // MAC address
                    list2.add(deviceName + "\n" + deviceHardwareAddress);
                }
            }
            final ArrayAdapter adapter = new ArrayAdapter(this,android.R.layout.simple_list_item_1, list2);
            listv.setAdapter(adapter);
           listv.setOnItemClickListener(myListClickListener);
            //Method called when the device from the list is clicked)



        }




    ///end/////////////
    }
    private AdapterView.OnItemClickListener myListClickListener = new AdapterView.OnItemClickListener()
    {
        public void onItemClick (AdapterView av, View v, int arg2, long arg3)
        {
            // Get the device MAC address, the last 17 chars in the View
            String info = ((TextView) v).getText().toString();
            String address = info.substring(info.length() - 17);
            // Make an intent to start next activity.
            Intent i = new Intent(MainActivity.this, Main2Activity.class);
            //Change the activity.
            //i.putExtra(EXTRA_ADDRESS, address); //this will be received at ledControl (class) Activity
            startActivity(i);
            //Toast.makeText(MainActivity.this, address, Toast.LENGTH_SHORT).show();
        }
    };


}