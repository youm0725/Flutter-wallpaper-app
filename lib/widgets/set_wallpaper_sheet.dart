import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';
import '../providers/set_wallpaper_provider.dart';
import '../services/wallpaper_service.dart';

/// Modal bottom sheet for setting wallpaper on Android and showing iOS manual workflow instructions.
class SetWallpaperSheet extends ConsumerStatefulWidget {
  final Wallpaper wallpaper;

  const SetWallpaperSheet({
    super.key,
    required this.wallpaper,
  });

  static void show(BuildContext context, Wallpaper wallpaper) {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => SetWallpaperSheet(wallpaper: wallpaper),
    );
  }

  @override
  ConsumerState<SetWallpaperSheet> createState() => _SetWallpaperSheetState();
}

class _SetWallpaperSheetState extends ConsumerState<SetWallpaperSheet> {
  bool _isProcessing = false;

  void _showFeedbackSnackBar(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(AppSizes.p16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSizes.radiusSm),
        ),
      ),
    );
  }

  Future<void> _handleApplyAndroid(WallpaperTarget target, String label) async {
    setState(() => _isProcessing = true);

    final success = await applyWallpaper(ref, widget.wallpaper, target);

    if (mounted) {
      setState(() => _isProcessing = false);
      Navigator.pop(context);
      _showFeedbackSnackBar(
        success
            ? 'Wallpaper applied to $label successfully'
            : 'Unable to set wallpaper',
      );
    }
  }

  Future<void> _handleApplyIos() async {
    setState(() => _isProcessing = true);

    await applyWallpaper(ref, widget.wallpaper, WallpaperTarget.both);

    if (mounted) {
      setState(() => _isProcessing = false);
      Navigator.pop(context);
      _showIosInstructionDialog(context);
    }
  }

  void _showIosInstructionDialog(BuildContext context) {
    final theme = Theme.of(context);

    showDialog<void>(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(
              Icons.check_circle_outline_rounded,
              color: theme.colorScheme.primary,
            ),
            const SizedBox(width: AppSizes.p8),
            const Expanded(child: Text('Saved to Photos')),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'iOS requires setting wallpapers directly through system settings:',
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: AppSizes.p12),
            _buildStepRow(context, '1', 'Open Apple Photos app'),
            const SizedBox(height: AppSizes.p6),
            _buildStepRow(context, '2', 'Select "${widget.wallpaper.title}"'),
            const SizedBox(height: AppSizes.p6),
            _buildStepRow(context, '3', 'Tap Share button -> "Use as Wallpaper"'),
          ],
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Got it'),
          ),
        ],
      ),
    );
  }

  Widget _buildStepRow(BuildContext context, String step, String text) {
    final theme = Theme.of(context);
    return Row(
      children: [
        CircleAvatar(
          radius: 10,
          backgroundColor: theme.colorScheme.primaryContainer,
          child: Text(
            step,
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.bold,
              color: theme.colorScheme.onPrimaryContainer,
            ),
          ),
        ),
        const SizedBox(width: AppSizes.p8),
        Expanded(
          child: Text(
            text,
            style: theme.textTheme.bodySmall?.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isIos = Platform.isIOS;

    return Container(
      padding: const EdgeInsets.all(AppSizes.p16),
      decoration: BoxDecoration(
        color: theme.scaffoldBackgroundColor,
        borderRadius: const BorderRadius.vertical(
          top: Radius.circular(AppSizes.radiusLg),
        ),
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40.0,
                height: 4.0,
                decoration: BoxDecoration(
                  color: theme.colorScheme.outline.withValues(alpha: 0.4),
                  borderRadius: BorderRadius.circular(2.0),
                ),
              ),
            ),
            const SizedBox(height: AppSizes.p16),
            Text(
              'Set Wallpaper',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: AppSizes.p4),
            Text(
              isIos
                  ? 'Save to Photos & follow step-by-step guidance'
                  : 'Choose where to apply this wallpaper',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: AppSizes.p16),
            if (_isProcessing)
              const Padding(
                padding: EdgeInsets.all(AppSizes.p24),
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              )
            else if (isIos) ...[
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.primaryContainer,
                  child: Icon(Icons.phonelink_setup_rounded,
                      color: theme.colorScheme.onPrimaryContainer),
                ),
                title: const Text('Save & Show Setup Guide'),
                subtitle: const Text('Apple Photos wallpaper workflow'),
                onTap: _handleApplyIos,
              ),
            ] else ...[
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  child: const Icon(Icons.home_outlined),
                ),
                title: const Text('Home Screen'),
                onTap: () => _handleApplyAndroid(
                    WallpaperTarget.homeScreen, 'Home Screen'),
              ),
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  child: const Icon(Icons.lock_outline_rounded),
                ),
                title: const Text('Lock Screen'),
                onTap: () => _handleApplyAndroid(
                    WallpaperTarget.lockScreen, 'Lock Screen'),
              ),
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: theme.colorScheme.surfaceContainerHighest,
                  child: const Icon(Icons.phonelink_setup_rounded),
                ),
                title: const Text('Home & Lock Screen'),
                onTap: () => _handleApplyAndroid(
                    WallpaperTarget.both, 'Home & Lock Screen'),
              ),
            ],
            const SizedBox(height: AppSizes.p16),
          ],
        ),
      ),
    );
  }
}
