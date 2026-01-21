package com.example.bluetooth

import android.content.Context
import android.os.Environment
import org.json.JSONArray
import java.io.File

/**
 * Mock Bluetooth device data class
 */
data class MockBluetoothDevice(
    val address: String,
    val name: String,
    val rssi: Int?,
    val firstSeen: String?,
    val lastSeen: String?,
    val timesSeen: Int
)

/**
 * Manager class to load mock Bluetooth devices from JSON file.
 * 
 * Usage:
 *   val manager = MockBluetoothManager(context)
 *   val devices = manager.getMockDevices()
 *   
 *   // Or check if mock data exists
 *   if (manager.hasMockData()) {
 *       // Use mock data instead of real Bluetooth scanning
 *   }
 */
class MockBluetoothManager(private val context: Context) {
    
    companion object {
        // Path where the Python script pushes the JSON file
        private const val MOCK_FILE_NAME = "mock_bluetooth_devices.json"
        
        // Check if we should use mock data (set this in BuildConfig or preferences)
        var USE_MOCK_DATA = true // Set to false for production
    }
    
    /**
     * Get the path to the mock data file
     */
    private fun getMockFilePath(): File {
        val downloadsDir = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_DOWNLOADS
        )
        return File(downloadsDir, MOCK_FILE_NAME)
    }
    
    /**
     * Check if mock data file exists
     */
    fun hasMockData(): Boolean {
        return getMockFilePath().exists()
    }
    
    /**
     * Load mock devices from JSON file
     */
    fun getMockDevices(): List<MockBluetoothDevice> {
        val file = getMockFilePath()
        
        if (!file.exists()) {
            return emptyList()
        }
        
        return try {
            val jsonString = file.readText()
            parseDevicesJson(jsonString)
        } catch (e: Exception) {
            e.printStackTrace()
            emptyList()
        }
    }
    
    /**
     * Parse JSON array of devices
     */
    private fun parseDevicesJson(jsonString: String): List<MockBluetoothDevice> {
        val devices = mutableListOf<MockBluetoothDevice>()
        val jsonArray = JSONArray(jsonString)
        
        for (i in 0 until jsonArray.length()) {
            val obj = jsonArray.getJSONObject(i)
            
            devices.add(
                MockBluetoothDevice(
                    address = obj.getString("address"),
                    name = obj.optString("name", "Unknown"),
                    rssi = if (obj.isNull("rssi")) null else obj.getInt("rssi"),
                    firstSeen = obj.optString("firstSeen", null),
                    lastSeen = obj.optString("lastSeen", null),
                    timesSeen = obj.optInt("timesSeen", 1)
                )
            )
        }
        
        return devices
    }
}
