import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../models/wallpaper.dart';
import '../../providers/recently_viewed_provider.dart';
import '../../providers/wallpaper_providers.dart';
import '../../widgets/widgets.dart';

/// Premium Wallpaper Details Screen featuring zoomable preview, fullscreen mode,
/// device preview modal, metadata, add-to-collection, and similar wallpapers.
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
  bool _isFullscreenMode = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref
          .read(recentlyViewedNotifierProvider.notifier)
          .addWallpaperView(widget.wallpaperId);
    });
  }

  void _toggleFullscreenMode() {
    setState(() {
      _isFullscreenMode = !_isFullscreenMode;
    });
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

          // Animated Floating Transparent AppBar
          AnimatedPositioned(
            duration: const Duration(milliseconds: 200),
            curve: Curves.easeInOut,
            top: _isFullscreenMode ? -100.0 : 0.0,
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
                      icon: Icons.bookmark_add_outlined,
                      tooltip: 'Add to Collection',
                      onTap: () {
                        AddToCollectionSheet.show(context, wallpaper);
                      },
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),

      // Animated Bottom Action Area
      bottomNavigationBar: _isFullscreenMode
          ? null
          : SafeArea(
              child: WallpaperActionBar(
                onDevicePreviewTap: () {
                  PhonePreviewWidget.showModal(context, wallpaper);
                },
              ),
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
          ZoomableWallpaper(
            wallpaper: wallpaper,
            height: _isFullscreenMode
                ? MediaQuery.of(context).size.height
                : 500.0,
            onTap: _toggleFullscreenMode,
          ),

          if (!_isFullscreenMode) ...[
            // Metadata Details Container
            Padding(
              padding: const EdgeInsets.all(AppSizes.p16),
              child: WallpaperMetadataCard(wallpaper: wallpaper),
            ),

            // Similar Wallpapers Section
            SimilarWallpapersSection(wallpaper: wallpaper),

            const SizedBox(height: AppSizes.p24),
          ],
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
              child: ZoomableWallpaper(
                wallpaper: wallpaper,
                height: double.infinity,
                onTap: _toggleFullscreenMode,
              ),
            ),
          ),
        ),

        // Right Column: Scrollable Metadata & Similar Section
        if (!_isFullscreenMode)
          Expanded(
            flex: 4,
            child: SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(AppSizes.p24),
                physics: const BouncingScrollPhysics(),
                child: Column(
                  children: [
                    WallpaperMetadataCard(wallpaper: wallpaper),
                    const SizedBox(height: AppSizes.p16),
                    SimilarWallpapersSection(wallpaper: wallpaper),
                  ],
                ),
              ),
            ),
          ),
      ],
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
