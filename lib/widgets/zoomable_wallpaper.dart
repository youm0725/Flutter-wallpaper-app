import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/wallpaper.dart';

/// Reusable zoomable wallpaper viewer widget supporting pinch-to-zoom,
/// double-tap zoom toggling, single-tap callbacks, and Hero animations.
class ZoomableWallpaper extends StatefulWidget {
  final Wallpaper wallpaper;
  final double height;
  final VoidCallback? onTap;

  const ZoomableWallpaper({
    super.key,
    required this.wallpaper,
    this.height = double.infinity,
    this.onTap,
  });

  @override
  State<ZoomableWallpaper> createState() => _ZoomableWallpaperState();
}

class _ZoomableWallpaperState extends State<ZoomableWallpaper>
    with SingleTickerProviderStateMixin {
  final TransformationController _transformationController =
      TransformationController();
  TapDownDetails? _doubleTapDetails;

  @override
  void dispose() {
    _transformationController.dispose();
    super.dispose();
  }

  void _handleDoubleTapDown(TapDownDetails details) {
    _doubleTapDetails = details;
  }

  void _handleDoubleTap() {
    if (_transformationController.value != Matrix4.identity()) {
      _transformationController.value = Matrix4.identity();
    } else {
      final position = _doubleTapDetails?.localPosition ?? Offset.zero;
      // ignore: deprecated_member_use
      _transformationController.value = Matrix4.identity()
        // ignore: deprecated_member_use
        ..translate(-position.dx * 1.5, -position.dy * 1.5)
        // ignore: deprecated_member_use
        ..scale(2.5, 2.5);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GestureDetector(
      onTap: widget.onTap,
      onDoubleTapDown: _handleDoubleTapDown,
      onDoubleTap: _handleDoubleTap,
      child: SizedBox(
        height: widget.height,
        width: double.infinity,
        child: InteractiveViewer(
          transformationController: _transformationController,
          minScale: 1.0,
          maxScale: 4.0,
          clipBehavior: Clip.none,
          child: Hero(
            tag: 'wallpaper_${widget.wallpaper.id}',
            child: Image.asset(
              widget.wallpaper.imagePath,
              fit: BoxFit.cover,
              frameBuilder: (context, child, frame, wasSynchronouslyLoaded) {
                if (wasSynchronouslyLoaded) return child;
                return AnimatedOpacity(
                  opacity: frame == null ? 0 : 1,
                  duration: const Duration(milliseconds: 250),
                  curve: Curves.easeOut,
                  child: child,
                );
              },
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  color: theme.colorScheme.surfaceContainerHighest,
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          Icons.image_outlined,
                          size: AppSizes.iconLg * 1.5,
                          color: theme.colorScheme.onSurfaceVariant
                              .withValues(alpha: 0.4),
                        ),
                        const SizedBox(height: AppSizes.p8),
                        Text(
                          widget.wallpaper.title,
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                            fontWeight: FontWeight.w600,
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
    );
  }
}
