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
      home: Scaffold(
        appBar: AppBar(title: const Text("TEOAE Controller")),
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
  String _status = "Ready to measure";
  String _result = "-- dB";
  bool _isLoading = false;

  // 10.0.2.2 is the special IP address that points to your PC's Localhost
  final String serverUrl = "http://192.168.0.29:5000/run_teoae";

  Future<void> runTest() async {
    setState(() {
      _isLoading = true;
      _status = "Measuring...";
    });

    try {
      final response = await http.get(Uri.parse(serverUrl));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _status = data['message'];
          _result = "${data['spl']} dB";
        });
      } else {
        setState(() {
          _status = "Server Error: ${response.statusCode}";
        });
      }
    } catch (e) {
      setState(() {
        _status = "Connection Failed. Is server running?";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text("TEOAE Result", style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          SizedBox(height: 20),
          Text(_result, style: TextStyle(fontSize: 48, color: Colors.blue)),
          SizedBox(height: 40),
          Text(_status, style: TextStyle(color: Colors.grey)),
          SizedBox(height: 20),
          ElevatedButton(
            onPressed: _isLoading ? null : runTest,
            style: ElevatedButton.styleFrom(
              padding: EdgeInsets.symmetric(horizontal: 40, vertical: 20),
            ),
            child: _isLoading 
                ? CircularProgressIndicator(color: Colors.white) 
                : Text("RUN TEST", style: TextStyle(fontSize: 18)),
          ),
        ],
      ),
    );
  }
}