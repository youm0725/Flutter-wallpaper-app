import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';
import 'wallpaper_card.dart';

/// Reusable horizontal scrollable list of wallpaper cards.
class HorizontalWallpaperList extends StatelessWidget {
  final List<Wallpaper> wallpapers;
  final Function(Wallpaper wallpaper) onWallpaperTap;
  final double height;

  const HorizontalWallpaperList({
    super.key,
    required this.wallpapers,
    required this.onWallpaperTap,
    this.height = 200.0,
  });

  @override
  Widget build(BuildContext context) {
    if (wallpapers.isEmpty) {
      return const SizedBox.shrink();
    }

    return SizedBox(
      height: height,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        physics: const BouncingScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: AppSizes.p16),
        itemCount: wallpapers.length,
        itemBuilder: (context, index) {
          final wallpaper = wallpapers[index];
          return Container(
            width: 140.0,
            margin: const EdgeInsets.only(right: AppSizes.p12),
            child: WallpaperCard(
              wallpaper: wallpaper,
              onTap: () => onWallpaperTap(wallpaper),
            ),
          );
        },
      ),
    );
  }
}
