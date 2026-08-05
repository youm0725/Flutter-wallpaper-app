import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_sizes.dart';

/// Minimal, elegant Splash Screen placeholder.
class SplashScreen extends StatelessWidget {
  const SplashScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.wallpaper_rounded,
              size: AppSizes.iconLg,
              color: AppColors.primary,
            ),
            SizedBox(height: AppSizes.p16),
            Text(
              'Wallpaper Gallery',
              style: TextStyle(
                fontSize: 20.0,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.5,
                color: AppColors.onBackground,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
