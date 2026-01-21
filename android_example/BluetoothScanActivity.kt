package com.example.bluetooth

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.widget.ArrayAdapter
import android.widget.ListView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

/**
 * Example Activity showing how to use mock Bluetooth data
 * when running on emulator, and real scanning on physical devices.
 */
class BluetoothScanActivity : AppCompatActivity() {
    
    private lateinit var mockManager: MockBluetoothManager
    private lateinit var deviceListAdapter: ArrayAdapter<String>
    private val deviceList = mutableListOf<String>()
    
    private var bluetoothAdapter: BluetoothAdapter? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // setContentView(R.layout.activity_bluetooth_scan)
        
        mockManager = MockBluetoothManager(this)
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter()
        
        // Setup list adapter
        deviceListAdapter = ArrayAdapter(this, android.R.layout.simple_list_item_1, deviceList)
        // findViewById<ListView>(R.id.deviceListView).adapter = deviceListAdapter
        
        // Decide whether to use mock or real data
        if (shouldUseMockData()) {
            loadMockDevices()
        } else {
            startRealBluetoothScan()
        }
    }
    
    /**
     * Determine if we should use mock data.
     * Use mock data if:
     * - Mock mode is enabled AND mock file exists
     * - OR we're on an emulator (no real Bluetooth)
     */
    private fun shouldUseMockData(): Boolean {
        // Check if Bluetooth is available (emulators typically don't have it)
        if (bluetoothAdapter == null) {
            Log.d("Bluetooth", "No Bluetooth adapter - using mock data")
            return true
        }
        
        // Check if mock mode is enabled and data exists
        if (MockBluetoothManager.USE_MOCK_DATA && mockManager.hasMockData()) {
            Log.d("Bluetooth", "Mock mode enabled - using mock data")
            return true
        }
        
        return false
    }
    
    /**
     * Load devices from mock JSON file
     */
    private fun loadMockDevices() {
        val devices = mockManager.getMockDevices()
        
        if (devices.isEmpty()) {
            Toast.makeText(this, "No mock devices found", Toast.LENGTH_SHORT).show()
            return
        }
        
        deviceList.clear()
        devices.forEach { device ->
            val displayText = "${device.name}\n${device.address}"
            deviceList.add(displayText)
        }
        deviceListAdapter.notifyDataSetChanged()
        
        Toast.makeText(
            this, 
            "Loaded ${devices.size} mock devices", 
            Toast.LENGTH_SHORT
        ).show()
        
        Log.d("Bluetooth", "Loaded ${devices.size} mock devices:")
        devices.forEach { 
            Log.d("Bluetooth", "  - ${it.name} (${it.address})")
        }
    }
    
    /**
     * Start real Bluetooth discovery (for physical devices)
     */
    private fun startRealBluetoothScan() {
        // Check permissions
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_SCAN) 
            != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(
                    Manifest.permission.BLUETOOTH_SCAN,
                    Manifest.permission.BLUETOOTH_CONNECT,
                    Manifest.permission.ACCESS_FINE_LOCATION
                ),
                REQUEST_BLUETOOTH_PERMISSIONS
            )
            return
        }
        
        // Register receiver for discovered devices
        val filter = IntentFilter(BluetoothDevice.ACTION_FOUND)
        registerReceiver(bluetoothReceiver, filter)
        
        // Start discovery
        bluetoothAdapter?.startDiscovery()
        Toast.makeText(this, "Scanning for Bluetooth devices...", Toast.LENGTH_SHORT).show()
    }
    
    /**
     * Receiver for real Bluetooth device discovery
     */
    private val bluetoothReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == BluetoothDevice.ACTION_FOUND) {
                val device: BluetoothDevice? = 
                    intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                
                device?.let {
                    val deviceName = it.name ?: "Unknown"
                    val deviceAddress = it.address
                    val displayText = "$deviceName\n$deviceAddress"
                    
                    if (!deviceList.contains(displayText)) {
                        deviceList.add(displayText)
                        deviceListAdapter.notifyDataSetChanged()
                    }
                }
            }
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(bluetoothReceiver)
        } catch (e: IllegalArgumentException) {
            // Receiver not registered
        }
        bluetoothAdapter?.cancelDiscovery()
    }
    
    companion object {
        private const val REQUEST_BLUETOOTH_PERMISSIONS = 1001
    }
}
