import 'package:flutter/material.dart';

/// Wallpaper Details Screen placeholder.
class WallpaperDetailsScreen extends StatelessWidget {
  final String wallpaperId;

  const WallpaperDetailsScreen({
    super.key,
    required this.wallpaperId,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Wallpaper Details ($wallpaperId)'),
      ),
      body: Center(
        child: Text(
          'Wallpaper Details ($wallpaperId) Coming Soon',
          style: const TextStyle(fontSize: 16.0),
        ),
      ),
    );
  }
}
