import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(
          title: const Text("TEOAE System"),
          backgroundColor: Colors.teal,
        ),
        body: const TeoaeControlScreen(),
      ),
    );
  }
}

class TeoaeControlScreen extends StatefulWidget {
  const TeoaeControlScreen({super.key});

  @override
  State<TeoaeControlScreen> createState() => _TeoaeControlScreenState();
}

class _TeoaeControlScreenState extends State<TeoaeControlScreen> {
  String _infoText = "Ready";
  String _bigNumber = "--";
  bool _isLoading = false;

  // CONFIRM THIS IP IS STILL CORRECT!
  final String baseUrl = "http://192.168.0.29:5000"; 

  Future<void> runStep(String endpoint, String label) async {
    setState(() {
      _isLoading = true;
      _infoText = "$label...";
    });

    try {
      final response = await http.get(Uri.parse("$baseUrl$endpoint"));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _infoText = data['message'];
          _bigNumber = data['value']; // Just the number
        });
      } else {
        setState(() { _infoText = "Error: ${response.statusCode}"; });
      }
    } catch (e) {
      setState(() { _infoText = "Connection Failed"; });
    } finally {
      setState(() { _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(20.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // DISPLAY AREA
          Container(
            padding: EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(10),
            ),
            child: Column(
              children: [
                Text(_infoText, style: TextStyle(fontSize: 16, color: Colors.black54)),
                SizedBox(height: 10),
                Text(
                  "$_bigNumber dB", 
                  style: TextStyle(fontSize: 50, fontWeight: FontWeight.bold, color: Colors.teal)
                ),
              ],
            ),
          ),
          
          SizedBox(height: 40),
          
          // BUTTON 1: MIC CALIBRATION
          ElevatedButton(
            onPressed: _isLoading ? null : () => runStep("/step1_calibrate_mic", "Calibrating Mic"),
            child: Text("1. CALIBRATE MIC (94dB)"),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.all(15),
              backgroundColor: Colors.grey[700],
              foregroundColor: Colors.white,
            ),
          ),
          
          SizedBox(height: 15),

          // BUTTON 2: SPEAKER CHECK
          ElevatedButton(
            onPressed: _isLoading ? null : () => runStep("/step2_check_speaker", "Checking Speaker"),
            child: Text("2. CHECK SPEAKER (Tone)"),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.all(15),
              backgroundColor: Colors.orange[800],
              foregroundColor: Colors.white,
            ),
          ),

          SizedBox(height: 15),

          // BUTTON 3: TEOAE TEST
          ElevatedButton(
            onPressed: _isLoading ? null : () => runStep("/step3_run_teoae", "Measuring TEOAE"),
            child: Text("3. RUN TEOAE TEST"),
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.all(20),
              backgroundColor: Colors.blue[800],
              foregroundColor: Colors.white,
              textStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
          ),
        ],
      ),
    );
  }
}