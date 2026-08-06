import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';

/// Reusable, refined wallpaper card component.
class WallpaperCard extends StatelessWidget {
  final Wallpaper wallpaper;
  final VoidCallback? onTap;

  const WallpaperCard({
    super.key,
    required this.wallpaper,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

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
              // Image Thumbnail with ClipRRect
              Expanded(
                child: ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(AppSizes.radiusMd - 1),
                  ),
                  child: Container(
                    width: double.infinity,
                    color: theme.colorScheme.surfaceContainerHighest,
                    child: Image.asset(
                      wallpaper.imagePath,
                      fit: BoxFit.cover,
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
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.image_outlined,
                                  size: AppSizes.iconLg - 8,
                                  color: theme.colorScheme.onSurfaceVariant
                                      .withValues(alpha: 0.5),
                                ),
                                const SizedBox(height: AppSizes.p4),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: AppSizes.p8,
                                    vertical: AppSizes.p4,
                                  ),
                                  decoration: BoxDecoration(
                                    color: theme.colorScheme.surface.withValues(alpha: 0.7),
                                    borderRadius: BorderRadius.circular(AppSizes.radiusSm - 2),
                                  ),
                                  child: Text(
                                    wallpaper.category.toUpperCase(),
                                    style: theme.textTheme.labelSmall?.copyWith(
                                      color: theme.colorScheme.onSurface,
                                      fontWeight: FontWeight.w700,
                                      letterSpacing: 0.8,
                                      fontSize: 10.0,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),
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
