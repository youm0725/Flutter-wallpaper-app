import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';

/// Reusable device preview widget displaying wallpaper inside a sleek phone bezel silhouette.
class PhonePreviewWidget extends StatelessWidget {
  final Wallpaper wallpaper;

  const PhonePreviewWidget({
    super.key,
    required this.wallpaper,
  });

  /// Static helper to display the preview inside a clean modal bottom sheet.
  static void showModal(BuildContext context, Wallpaper wallpaper) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return Container(
          height: MediaQuery.of(context).size.height * 0.85,
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
            borderRadius: const BorderRadius.vertical(
              top: Radius.circular(AppSizes.radiusLg),
            ),
          ),
          child: Column(
            children: [
              const SizedBox(height: AppSizes.p12),
              // Drag Handle
              Container(
                width: 40.0,
                height: 4.0,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(AppSizes.p4),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(AppSizes.p16),
                child: Text(
                  'Device Preview',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                ),
              ),
              Expanded(
                child: Center(
                  child: PhonePreviewWidget(wallpaper: wallpaper),
                ),
              ),
              const SizedBox(height: AppSizes.p24),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final frameBorderColor = isDark
        ? const Color(0xFF334155)
        : const Color(0xFF0F172A);

    return AspectRatio(
      aspectRatio: 9 / 19.5, // Standard modern smartphone aspect ratio
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: AppSizes.p24),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(32.0),
          border: Border.all(
            color: frameBorderColor,
            width: 8.0,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.15),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(24.0),
          child: Stack(
            fit: StackFit.expand,
            children: [
              // Wallpaper Image Background
              Image.asset(
                wallpaper.imagePath,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    color: theme.colorScheme.surfaceContainerHighest,
                    child: Center(
                      child: Icon(
                        Icons.wallpaper_rounded,
                        size: AppSizes.iconLg,
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  );
                },
              ),

              // Subtle Dark Overlay Tint for UI Legibility
              Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      Colors.black.withValues(alpha: 0.4),
                      Colors.transparent,
                      Colors.black.withValues(alpha: 0.2),
                    ],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                ),
              ),

              // Camera Punch Hole Cutout Notch
              Positioned(
                top: 8.0,
                left: 0,
                right: 0,
                child: Center(
                  child: Container(
                    width: 12.0,
                    height: 12.0,
                    decoration: const BoxDecoration(
                      color: Colors.black,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
              ),

              // Lockscreen / Homescreen Status Clock Overlay
              Positioned(
                top: 36.0,
                left: 0,
                right: 0,
                child: Column(
                  children: [
                    const Text(
                      '09:41',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 42.0,
                        fontWeight: FontWeight.w300,
                        letterSpacing: -1.0,
                        shadows: [
                          Shadow(
                            blurRadius: 10.0,
                            color: Colors.black45,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 2.0),
                    Text(
                      'Thursday, August 6',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.9),
                        fontSize: 12.0,
                        fontWeight: FontWeight.w500,
                        shadows: const [
                          Shadow(
                            blurRadius: 8.0,
                            color: Colors.black45,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // Bottom Gesture Bar Indicator
              Positioned(
                bottom: 8.0,
                left: 0,
                right: 0,
                child: Center(
                  child: Container(
                    width: 100.0,
                    height: 4.0,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.8),
                      borderRadius: BorderRadius.circular(2.0),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
