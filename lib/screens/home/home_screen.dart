import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

/// Home Screen placeholder.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Wallpaper Gallery'),
      ),
      body: const Center(
        child: Text(
          'Home Screen Placeholder',
          style: TextStyle(
            fontSize: 16.0,
            color: AppColors.onSurfaceVariant,
          ),
        ),
      ),
    );
  }
}
