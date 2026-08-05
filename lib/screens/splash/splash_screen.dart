import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';

/// Minimal, elegant Splash Screen that navigates to HomeScreen after initialization.
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateToHome();
  }

  Future<void> _navigateToHome() async {
    await Future<void>.delayed(const Duration(milliseconds: 1500));
    if (mounted) {
      context.go(RouteConstants.homePath);
    }
  }

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
