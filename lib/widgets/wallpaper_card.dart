import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';
import '../providers/favorites_provider.dart';

/// Reusable, refined wallpaper card component with favorite status indicator.
class WallpaperCard extends ConsumerWidget {
  final Wallpaper wallpaper;
  final VoidCallback? onTap;

  const WallpaperCard({
    super.key,
    required this.wallpaper,
    this.onTap,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    // .select() ensures this card only rebuilds when THIS wallpaper's
    // favorite status changes — not when any other wallpaper is toggled.
    final isFav = ref.watch(
      favoritesNotifierProvider.select(
        (asyncValue) => asyncValue.value?.contains(wallpaper.id) ?? false,
      ),
    );

    final backgroundColor = isDark
        ? theme.colorScheme.surface
        : theme.colorScheme.surface;

    final borderColor = theme.colorScheme.outline.withValues(alpha: 0.25);

    return Material(
      color: backgroundColor,
      borderRadius: BorderRadius.circular(AppSizes.radiusMd),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppSizes.radiusMd),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(AppSizes.radiusMd),
            border: Border.all(
              color: borderColor,
              width: 1.0,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Image Thumbnail with Hero, ClipRRect, and Favorite Badge
              Expanded(
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Hero(
                      tag: 'wallpaper_${wallpaper.id}',
                      child: ClipRRect(
                        borderRadius: const BorderRadius.vertical(
                          top: Radius.circular(AppSizes.radiusMd - 1),
                        ),
                        child: Container(
                          width: double.infinity,
                          color: theme.colorScheme.surfaceContainerHighest,
                          child: Image.asset(
                            wallpaper.effectiveThumbnailPath,
                            fit: BoxFit.cover,
                            // Limit decoded image size to thumbnail dimensions,
                            // significantly reducing memory usage for grid display.
                            cacheWidth: 400,
                            errorBuilder: (context, error, stackTrace) {
                              return Container(
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    colors: [
                                      theme.colorScheme.primaryContainer,
                                      theme.colorScheme.surfaceContainerHighest,
                                    ],
                                    begin: Alignment.topLeft,
                                    end: Alignment.bottomRight,
                                  ),
                                ),
                                child: Center(
                                  child: Icon(
                                    Icons.image_outlined,
                                    size: AppSizes.iconLg - 8,
                                    color: theme.colorScheme.onSurfaceVariant
                                        .withValues(alpha: 0.5),
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
                      ),
                    ),

                    // Top Right Favorite Quick Button Indicator
                    Positioned(
                      top: AppSizes.p6,
                      right: AppSizes.p6,
                      child: Material(
                        color: Colors.black.withValues(alpha: 0.45),
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: () {
                            ref
                                .read(favoritesNotifierProvider.notifier)
                                .toggleFavorite(wallpaper.id);
                          },
                          child: Padding(
                            padding: const EdgeInsets.all(AppSizes.p6),
                            child: Icon(
                              isFav
                                  ? Icons.favorite_rounded
                                  : Icons.favorite_outline_rounded,
                              size: 16.0,
                              color: isFav
                                  ? Colors.redAccent
                                  : Colors.white.withValues(alpha: 0.9),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // Title and details section
              Padding(
                padding: const EdgeInsets.all(AppSizes.p12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      wallpaper.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: theme.textTheme.titleSmall?.copyWith(
                        fontWeight: FontWeight.w700,
                        letterSpacing: -0.2,
                      ),
                    ),
                    const SizedBox(height: AppSizes.p4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Flexible(
                          child: Text(
                            wallpaper.category[0].toUpperCase() +
                                wallpaper.category.substring(1),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                        const SizedBox(width: AppSizes.p4),
                        Text(
                          wallpaper.resolution,
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant
                                .withValues(alpha: 0.7),
                            fontSize: 10.0,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
