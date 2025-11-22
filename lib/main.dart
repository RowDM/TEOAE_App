import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:fl_chart/fl_chart.dart'; // THE CHART LIBRARY

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.teal,
        scaffoldBackgroundColor: Colors.grey[100],
      ),
      home: Scaffold(
        appBar: AppBar(
          title: const Text("TEOAE Clinical Monitor"),
          backgroundColor: Colors.teal[800],
          centerTitle: true,
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
  String _infoText = "System Ready";
  String _bigNumber = "--";
  bool _isLoading = false;
  List<double> _waveform = []; // Stores the graph data

  // UPDATE YOUR IP HERE
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
        
        // Check if we received waveform data (Step 3 only)
        List<double> newWave = [];
        if (data.containsKey('data')) {
          newWave = List<double>.from(data['data'].map((x) => x as double));
        }

        setState(() {
          _infoText = data['message'];
          _bigNumber = data['value'];
          if (newWave.isNotEmpty) {
            _waveform = newWave;
          }
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
    return Column(
      children: [
        // === TOP SECTION: THE GRAPH (Medical Look) ===
        Expanded(
          flex: 4, // Takes up 40% of screen
          child: Container(
            color: Colors.black, // Oscilloscope background
            padding: const EdgeInsets.all(10),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("RESPONSE WAVEFORM (ms)", style: TextStyle(color: Colors.tealAccent, fontSize: 12)),
                Expanded(
                  child: _waveform.isEmpty 
                    ? Center(child: Text("NO SIGNAL", style: TextStyle(color: Colors.grey[800])))
                    : LineChart(
                        LineChartData(
                          gridData: FlGridData(show: true, drawVerticalLine: false, getDrawingHorizontalLine: (value) => FlLine(color: Colors.grey[900], strokeWidth: 1)),
                          titlesData: FlTitlesData(show: false),
                          borderData: FlBorderData(show: true, border: Border.all(color: Colors.grey[800]!)),
                          lineBarsData: [
                            LineChartBarData(
                              spots: _waveform.asMap().entries.map((e) {
                                return FlSpot(e.key.toDouble(), e.value);
                              }).toList(),
                              isCurved: false,
                              color: Colors.tealAccent, // The "Medical Green" line
                              dotData: FlDotData(show: false),
                              belowBarData: BarAreaData(show: false),
                              barWidth: 2,
                            ),
                          ],
                        ),
                      ),
                ),
              ],
            ),
          ),
        ),

        // === MIDDLE SECTION: THE RESULT ===
        Expanded(
          flex: 2,
          child: Container(
            color: Colors.white,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text("STATUS", style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                    Text(_infoText, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
                  ],
                ),
                Container(width: 1, height: 50, color: Colors.grey[300]),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text("TEOAE LEVEL", style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
                    Text("$_bigNumber dB", style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.teal[800])),
                  ],
                ),
              ],
            ),
          ),
        ),

        // === BOTTOM SECTION: BUTTONS ===
        Expanded(
          flex: 4,
          child: Container(
            padding: EdgeInsets.all(20),
            color: Colors.grey[50],
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                 _buildButton("1. CALIBRATE MIC (94dB)", Colors.grey, () => runStep("/step1_calibrate_mic", "Calibrating")),
                 _buildButton("2. CHECK SPEAKER (Tone)", Colors.orange, () => runStep("/step2_check_speaker", "Checking Speaker")),
                 _buildButton("3. RUN TEOAE TEST", Colors.blue[800]!, () => runStep("/step3_run_teoae", "Measuring")),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildButton(String text, Color color, VoidCallback tapHandler) {
    return ElevatedButton(
      onPressed: _isLoading ? null : tapHandler,
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: EdgeInsets.symmetric(vertical: 15),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        elevation: 2,
      ),
      child: Text(text, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
    );
  }
}