import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';
import '../providers/download_provider.dart';

/// Reusable action bar for wallpaper details screen with interactive download functionality.
class WallpaperActionBar extends ConsumerWidget {
  final Wallpaper wallpaper;
  final VoidCallback? onDevicePreviewTap;

  const WallpaperActionBar({
    super.key,
    required this.wallpaper,
    this.onDevicePreviewTap,
  });

  void _showFeedbackSnackBar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(AppSizes.p16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        ),
      ),
    );
  }

  void _showComingSoonSnackBar(BuildContext context) {
    _showFeedbackSnackBar(context, 'Coming Soon');
  }

  Future<void> _handleDownload(BuildContext context, WidgetRef ref) async {
    final activeDownloads = ref.read(activeDownloadsProvider);
    if (activeDownloads.contains(wallpaper.id)) return;

    final result = await downloadWallpaper(ref, wallpaper);

    if (!context.mounted) return;

    switch (result) {
      case DownloadResult.success:
        _showFeedbackSnackBar(
          context,
          'Wallpaper "${wallpaper.title}" saved to Gallery',
        );
        break;
      case DownloadResult.permissionDenied:
        _showFeedbackSnackBar(
          context,
          'Storage permission required to save wallpaper',
        );
        break;
      case DownloadResult.error:
        _showFeedbackSnackBar(
          context,
          'Unable to save wallpaper. Please check permissions.',
        );
        break;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final activeDownloads = ref.watch(activeDownloadsProvider);
    final isDownloading = activeDownloads.contains(wallpaper.id);

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
          if (onDevicePreviewTap != null) ...[
            // Phone Frame Preview button
            _buildIconButton(
              context,
              icon: Icons.smartphone_rounded,
              tooltip: 'Device Preview',
              onTap: onDevicePreviewTap!,
            ),
            const SizedBox(width: AppSizes.p8),
          ],

          // Primary Download Button with Progress Indicator
          Expanded(
            child: OutlinedButton.icon(
              onPressed: isDownloading ? null : () => _handleDownload(context, ref),
              icon: isDownloading
                  ? const SizedBox(
                      width: 18.0,
                      height: 18.0,
                      child: CircularProgressIndicator(strokeWidth: 2.0),
                    )
                  : const Icon(Icons.download_rounded, size: AppSizes.iconSm + 2),
              label: Text(isDownloading ? 'Saving...' : 'Download'),
            ),
          ),
          const SizedBox(width: AppSizes.p8),

          Expanded(
            child: ElevatedButton.icon(
              onPressed: () => _showComingSoonSnackBar(context),
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
}
