import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';

/// Component displaying wallpaper metadata details and tags.
class WallpaperMetadataCard extends StatelessWidget {
  final Wallpaper wallpaper;

  const WallpaperMetadataCard({
    super.key,
    required this.wallpaper,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final cardBackgroundColor = isDark
        ? theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.4)
        : theme.colorScheme.surface;

    final borderColor = theme.colorScheme.outline.withValues(alpha: 0.25);

    return Container(
      padding: const EdgeInsets.all(AppSizes.p16),
      decoration: BoxDecoration(
        color: cardBackgroundColor,
        borderRadius: BorderRadius.circular(AppSizes.radiusMd),
        border: Border.all(
          color: borderColor,
          width: 1.0,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title & Category Header
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      wallpaper.title,
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.4,
                      ),
                    ),
                    const SizedBox(height: AppSizes.p4),
                    Text(
                      wallpaper.category[0].toUpperCase() +
                          wallpaper.category.substring(1),
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: AppSizes.p16),
          const Divider(),
          const SizedBox(height: AppSizes.p16),

          // Metadata Grid Info (Resolution & File Size)
          Row(
            children: [
              Expanded(
                child: _buildMetaTile(
                  context,
                  icon: Icons.aspect_ratio_rounded,
                  label: 'Resolution',
                  value: wallpaper.resolution,
                ),
              ),
              Container(
                height: 36.0,
                width: 1.0,
                color: theme.colorScheme.outline.withValues(alpha: 0.3),
              ),
              Expanded(
                child: _buildMetaTile(
                  context,
                  icon: Icons.sd_storage_outlined,
                  label: 'File Size',
                  value: wallpaper.fileSize,
                ),
              ),
            ],
          ),

          if (wallpaper.tags.isNotEmpty) ...[
            const SizedBox(height: AppSizes.p16),
            const Divider(),
            const SizedBox(height: AppSizes.p16),

            // Tags List
            Text(
              'Tags',
              style: theme.textTheme.labelMedium?.copyWith(
                fontWeight: FontWeight.w700,
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSizes.p8),
            Wrap(
              spacing: AppSizes.p8,
              runSpacing: AppSizes.p8,
              children: wallpaper.tags.map((tag) {
                return Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSizes.p12,
                    vertical: AppSizes.p6,
                  ),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(AppSizes.radiusSm),
                    border: Border.all(
                      color: theme.colorScheme.outline.withValues(alpha: 0.2),
                    ),
                  ),
                  child: Text(
                    '#$tag',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMetaTile(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
  }) {
    final theme = Theme.of(context);

    return Column(
      children: [
        Icon(
          icon,
          size: AppSizes.iconMd - 2,
          color: theme.colorScheme.onSurfaceVariant,
        ),
        const SizedBox(height: AppSizes.p4),
        Text(
          label,
          style: theme.textTheme.labelSmall?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
        const SizedBox(height: AppSizes.p2),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
      ],
    );
  }
}
