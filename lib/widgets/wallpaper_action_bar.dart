import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';

/// Reusable action bar for wallpaper details screen.
class WallpaperActionBar extends StatelessWidget {
  const WallpaperActionBar({super.key});

  void _showComingSoonSnackBar(BuildContext context, String actionName) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$actionName feature coming in future release'),
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

    final backgroundColor = isDark
        ? theme.colorScheme.surface
        : theme.colorScheme.surface;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSizes.p16,
        vertical: AppSizes.p12,
      ),
      decoration: BoxDecoration(
        color: backgroundColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
        border: Border(
          top: BorderSide(
            color: theme.colorScheme.outline.withValues(alpha: 0.2),
            width: 1.0,
          ),
        ),
      ),
      child: Row(
        children: [
          // Favorite button
          _buildIconButton(
            context,
            icon: Icons.favorite_outline_rounded,
            tooltip: 'Favorite',
            onTap: () => _showComingSoonSnackBar(context, 'Save Favorite'),
          ),
          const SizedBox(width: AppSizes.p8),

          // Share button
          _buildIconButton(
            context,
            icon: Icons.share_outlined,
            tooltip: 'Share',
            onTap: () => _showComingSoonSnackBar(context, 'Share'),
          ),
          const SizedBox(width: AppSizes.p12),

          // Primary Download & Set Wallpaper Buttons
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () => _showComingSoonSnackBar(context, 'Download'),
              icon: const Icon(Icons.download_rounded, size: AppSizes.iconSm + 2),
              label: const Text('Download'),
            ),
          ),
          const SizedBox(width: AppSizes.p8),

          Expanded(
            child: ElevatedButton.icon(
              onPressed: () => _showComingSoonSnackBar(context, 'Set Wallpaper'),
              icon: const Icon(Icons.wallpaper_rounded, size: AppSizes.iconSm + 2),
              label: const Text('Set Wallpaper'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildIconButton(
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
          width: 48.0,
          height: 48.0,
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
}
