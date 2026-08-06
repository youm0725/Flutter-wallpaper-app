import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../core/constants/app_sizes.dart';
import '../core/router/route_constants.dart';
import '../models/wallpaper.dart';
import '../providers/wallpaper_providers.dart';
import 'section_header.dart';

/// Reusable section component displaying similar wallpapers based on category/tag matching.
class SimilarWallpapersSection extends ConsumerWidget {
  final Wallpaper wallpaper;

  const SimilarWallpapersSection({
    super.key,
    required this.wallpaper,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final similarWallpapers = ref.watch(similarWallpapersProvider(wallpaper));

    if (similarWallpapers.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SectionHeader(
          title: 'Similar Wallpapers',
          subtitle: 'Based on category & tags',
        ),
        const SizedBox(height: AppSizes.p8),
        SizedBox(
          height: 180.0,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(horizontal: AppSizes.p16),
            itemCount: similarWallpapers.length,
            itemBuilder: (context, index) {
              final item = similarWallpapers[index];
              return Container(
                width: 120.0,
                margin: const EdgeInsets.only(right: AppSizes.p12),
                child: Material(
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(AppSizes.radiusMd),
                  clipBehavior: Clip.antiAlias,
                  child: InkWell(
                    onTap: () {
                      context.pushNamed(
                        RouteConstants.wallpaperDetailsName,
                        pathParameters: {'id': item.id},
                        extra: item,
                      );
                    },
                    child: Container(
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(AppSizes.radiusMd),
                        border: Border.all(
                          color: theme.colorScheme.outline.withValues(alpha: 0.25),
                          width: 1.0,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Image.asset(
                              item.effectiveThumbnailPath,
                              width: double.infinity,
                              fit: BoxFit.cover,
                              cacheWidth: 300,
                              errorBuilder: (context, error, stackTrace) {
                                return Container(
                                  color: theme.colorScheme.surfaceContainerHighest,
                                  child: Center(
                                    child: Icon(
                                      Icons.image_outlined,
                                      size: AppSizes.iconMd,
                                      color: theme.colorScheme.onSurfaceVariant,
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                          Padding(
                            padding: const EdgeInsets.all(AppSizes.p8),
                            child: Text(
                              item.title,
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: theme.textTheme.labelMedium?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}
