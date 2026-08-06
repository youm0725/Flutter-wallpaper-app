import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';

/// Component displaying wallpaper metadata details, action buttons beside name, and tags.
class WallpaperMetadataCard extends StatelessWidget {
  final Wallpaper wallpaper;

  const WallpaperMetadataCard({
    super.key,
    required this.wallpaper,
  });

  void _showComingSoonSnackBar(BuildContext context) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('Coming Soon'),
        duration: const Duration(seconds: 2),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(AppSizes.p16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        ),
      ),
    );
  }

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
          // Title & Category Header with Favorite and Share Buttons
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
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

              const SizedBox(width: AppSizes.p8),

              // Favorite Button beside name
              _buildActionButton(
                context,
                icon: Icons.favorite_outline_rounded,
                tooltip: 'Favorite',
                onTap: () => _showComingSoonSnackBar(context),
              ),

              const SizedBox(width: AppSizes.p8),

              // Share Button beside favorite button
              _buildActionButton(
                context,
                icon: Icons.share_outlined,
                tooltip: 'Share',
                onTap: () => _showComingSoonSnackBar(context),
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

  Widget _buildActionButton(
    BuildContext context, {
    required IconData icon,
    required String tooltip,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);

    return Material(
      color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.6),
      borderRadius: BorderRadius.circular(AppSizes.radiusSm),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        child: Container(
          width: 44.0,
          height: 44.0,
          alignment: Alignment.center,
          child: Icon(
            icon,
            size: AppSizes.iconMd - 2,
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
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
