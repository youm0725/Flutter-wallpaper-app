import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../models/wallpaper.dart';
import '../../providers/wallpaper_providers.dart';
import '../../widgets/widgets.dart';

/// Premium Wallpaper Details Screen featuring interactive zoom/pan image viewer and metadata.
class WallpaperDetailsScreen extends ConsumerStatefulWidget {
  final String wallpaperId;
  final Wallpaper? wallpaper;

  const WallpaperDetailsScreen({
    super.key,
    required this.wallpaperId,
    this.wallpaper,
  });

  @override
  ConsumerState<WallpaperDetailsScreen> createState() =>
      _WallpaperDetailsScreenState();
}

class _WallpaperDetailsScreenState
    extends ConsumerState<WallpaperDetailsScreen> {
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
    if (widget.wallpaper != null) {
      return _buildDetailsScaffold(context, widget.wallpaper!);
    }

    final asyncWallpapers = ref.watch(wallpapersProvider);

    return asyncWallpapers.when(
      data: (wallpapers) {
        final wallpaper = wallpapers.firstWhere(
          (w) => w.id == widget.wallpaperId,
          orElse: () => Wallpaper(
            id: widget.wallpaperId,
            title: 'Wallpaper',
            category: 'General',
            imagePath: '',
            resolution: 'Unknown',
            fileSize: 'Unknown',
            tags: const [],
          ),
        );
        return _buildDetailsScaffold(context, wallpaper);
      },
      loading: () => const Scaffold(
        body: LoadingView(message: 'Loading wallpaper details...'),
      ),
      error: (error, stack) => Scaffold(
        appBar: AppBar(),
        body: ErrorStateView(
          message: error.toString(),
          onRetry: () => ref.invalidate(wallpapersProvider),
        ),
      ),
    );
  }

  Widget _buildDetailsScaffold(BuildContext context, Wallpaper wallpaper) {
    final isLandscape =
        MediaQuery.of(context).orientation == Orientation.landscape;
    final isTablet = MediaQuery.of(context).size.width > 600;

    return Scaffold(
      body: Stack(
        children: [
          // Content View (Responsive Split or Vertical Scroll)
          if (isLandscape || isTablet)
            _buildLandscapeTabletLayout(context, wallpaper)
          else
            _buildPortraitLayout(context, wallpaper),

          // Floating Transparent AppBar
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSizes.p16,
                  vertical: AppSizes.p8,
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildFloatingIconButton(
                      context,
                      icon: Icons.arrow_back_rounded,
                      tooltip: 'Back',
                      onTap: () => context.pop(),
                    ),
                    _buildFloatingIconButton(
                      context,
                      icon: Icons.more_vert_rounded,
                      tooltip: 'Options',
                      onTap: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Options menu placeholder'),
                            duration: Duration(seconds: 1),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),

      // Bottom Action Area
      bottomNavigationBar: const SafeArea(
        child: WallpaperActionBar(),
      ),
    );
  }

  Widget _buildPortraitLayout(BuildContext context, Wallpaper wallpaper) {
    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Image Viewer Header
          _buildImageViewer(context, wallpaper, height: 480.0),

          // Metadata Details Container
          Padding(
            padding: const EdgeInsets.all(AppSizes.p16),
            child: WallpaperMetadataCard(wallpaper: wallpaper),
          ),

          const SizedBox(height: AppSizes.p16),
        ],
      ),
    );
  }

  Widget _buildLandscapeTabletLayout(
      BuildContext context, Wallpaper wallpaper) {
    return Row(
      children: [
        // Left Column: Large Image Viewer
        Expanded(
          flex: 5,
          child: Container(
            color: Colors.black,
            child: Center(
              child: _buildImageViewer(context, wallpaper,
                  height: double.infinity),
            ),
          ),
        ),

        // Right Column: Scrollable Metadata Details
        Expanded(
          flex: 4,
          child: SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(AppSizes.p24),
              physics: const BouncingScrollPhysics(),
              child: WallpaperMetadataCard(wallpaper: wallpaper),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildImageViewer(BuildContext context, Wallpaper wallpaper,
      {required double height}) {
    final theme = Theme.of(context);

    return GestureDetector(
      onDoubleTapDown: _handleDoubleTapDown,
      onDoubleTap: _handleDoubleTap,
      child: SizedBox(
        height: height,
        width: double.infinity,
        child: InteractiveViewer(
          transformationController: _transformationController,
          minScale: 1.0,
          maxScale: 4.0,
          clipBehavior: Clip.none,
          child: Hero(
            tag: 'wallpaper_${wallpaper.id}',
            child: Image.asset(
              wallpaper.imagePath,
              fit: BoxFit.cover,
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
                          wallpaper.title,
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

  Widget _buildFloatingIconButton(
    BuildContext context, {
    required IconData icon,
    required String tooltip,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);

    return Material(
      color: theme.colorScheme.surface.withValues(alpha: 0.85),
      shape: const CircleBorder(),
      elevation: 2,
      child: InkWell(
        onTap: onTap,
        customBorder: const CircleBorder(),
        child: Padding(
          padding: const EdgeInsets.all(AppSizes.p8 + 2),
          child: Icon(
            icon,
            size: AppSizes.iconMd - 2,
            color: theme.colorScheme.onSurface,
          ),
        ),
      ),
    );
  }
}
