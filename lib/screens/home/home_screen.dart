import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_sizes.dart';
import '../../providers/wallpaper_providers.dart';

/// Home Screen displaying wallpaper data loaded via Riverpod.
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncWallpapers = ref.watch(wallpapersProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Wallpaper Gallery'),
      ),
      body: asyncWallpapers.when(
        data: (wallpapers) {
          if (wallpapers.isEmpty) {
            return const Center(
              child: Text(
                'No wallpapers found.',
                style: TextStyle(
                  fontSize: 16.0,
                  color: AppColors.onSurfaceVariant,
                ),
              ),
            );
          }

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.all(AppSizes.p16),
                child: Text(
                  'Total Wallpapers: ${wallpapers.length}',
                  style: const TextStyle(
                    fontSize: 18.0,
                    fontWeight: FontWeight.w600,
                    color: AppColors.onBackground,
                  ),
                ),
              ),
              const Divider(),
              Expanded(
                child: ListView.separated(
                  itemCount: wallpapers.length,
                  separatorBuilder: (context, index) => const Divider(),
                  itemBuilder: (context, index) {
                    final wallpaper = wallpapers[index];
                    return ListTile(
                      title: Text(
                        wallpaper.title,
                        style: const TextStyle(
                          fontSize: 15.0,
                          fontWeight: FontWeight.w500,
                          color: AppColors.onSurface,
                        ),
                      ),
                      subtitle: Text(
                        'Category: ${wallpaper.category} | ${wallpaper.resolution}',
                        style: const TextStyle(
                          fontSize: 13.0,
                          color: AppColors.onSurfaceVariant,
                        ),
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(),
        ),
        error: (error, stackTrace) => Center(
          child: Padding(
            padding: const EdgeInsets.all(AppSizes.p16),
            child: Text(
              'Failed to load wallpapers: $error',
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 14.0,
                color: Colors.red,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
