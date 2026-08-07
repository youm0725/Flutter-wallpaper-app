import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../models/wallpaper.dart';
import '../../providers/download_provider.dart';
import '../../providers/favorites_provider.dart';
import '../../providers/wallpaper_providers.dart';
import '../../widgets/widgets.dart';

/// Full-screen, edge-to-edge wallpaper viewer with minimal floating controls matching reference UI.
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
  bool _showControls = true;

  void _toggleControls() {
    setState(() {
      _showControls = !_showControls;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (widget.wallpaper != null) {
      return _buildFullscreenViewer(context, widget.wallpaper!);
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
        return _buildFullscreenViewer(context, wallpaper);
      },
      loading: () => const Scaffold(
        backgroundColor: Colors.black,
        body: LoadingView(message: 'Loading full wallpaper...'),
      ),
      error: (error, stack) => Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(backgroundColor: Colors.black),
        body: ErrorStateView(
          message: error.toString(),
          onRetry: () => ref.invalidate(wallpapersProvider),
        ),
      ),
    );
  }

  Widget _buildFullscreenViewer(BuildContext context, Wallpaper wallpaper) {
    final asyncFavIds = ref.watch(favoritesNotifierProvider);
    final isFav = asyncFavIds.value?.contains(wallpaper.id) ?? false;
    final activeDownloads = ref.watch(activeDownloadsProvider);
    final isDownloading = activeDownloads.contains(wallpaper.id);

    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
        systemNavigationBarColor: Colors.transparent,
        systemNavigationBarDividerColor: Colors.transparent,
        systemNavigationBarIconBrightness: Brightness.light,
      ),
      child: Scaffold(
        backgroundColor: Colors.black,
        extendBodyBehindAppBar: true,
        extendBody: true,
        body: Stack(
          fit: StackFit.expand,
          children: [
            // 1. Full-screen Edge-to-Edge Wallpaper Image Viewer
            ZoomableWallpaper(
              wallpaper: wallpaper,
              height: double.infinity,
              onTap: _toggleControls,
            ),

            // 2. Top Floating Navigation Area (Back Button)
            AnimatedOpacity(
              opacity: _showControls ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeInOut,
              child: IgnorePointer(
                ignoring: !_showControls,
                child: SafeArea(
                  top: true,
                  bottom: false,
                  child: Align(
                    alignment: Alignment.topLeft,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppSizes.p16,
                        vertical: AppSizes.p8,
                      ),
                      child: Material(
                        color: Colors.black.withValues(alpha: 0.35),
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: () => context.pop(),
                          child: const Padding(
                            padding: EdgeInsets.all(AppSizes.p8),
                            child: Icon(
                              Icons.arrow_back_rounded,
                              size: 22.0,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),

            // 3. Bottom Floating Action Controls (Reference UI Alignment)
            AnimatedOpacity(
              opacity: _showControls ? 1.0 : 0.0,
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeInOut,
              child: IgnorePointer(
                ignoring: !_showControls,
                child: SafeArea(
                  top: false,
                  bottom: true,
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Padding(
                      padding: const EdgeInsets.only(
                        bottom: AppSizes.p16,
                        left: AppSizes.p24,
                        right: AppSizes.p24,
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          // 1. Info Button (i)
                          _buildOverlayIconButton(
                            icon: Icons.info_outline_rounded,
                            tooltip: 'Wallpaper Details',
                            onTap: () => _showInfoModal(context, wallpaper),
                          ),

                          // 2. Favorite Button (Heart)
                          _buildOverlayIconButton(
                            icon: isFav
                                ? Icons.favorite_rounded
                                : Icons.favorite_outline_rounded,
                            iconColor: isFav ? Colors.redAccent : Colors.white,
                            tooltip: isFav ? 'Remove Favorite' : 'Favorite',
                            onTap: () {
                              ref
                                  .read(favoritesNotifierProvider.notifier)
                                  .toggleFavorite(wallpaper.id);
                            },
                          ),

                          // 3. Save/Download Button (Disk / Save)
                          _buildOverlayIconButton(
                            icon: isDownloading
                                ? Icons.hourglass_top_rounded
                                : Icons.save_outlined,
                            tooltip: 'Save to Gallery',
                            onTap: () => _handleDownload(context, ref, wallpaper),
                          ),

                          // 4. Set Wallpaper Button (Shortcut / Apply)
                          _buildOverlayIconButton(
                            icon: Icons.shortcut_rounded,
                            tooltip: 'Set Wallpaper',
                            onTap: () {
                              SetWallpaperSheet.show(context, wallpaper);
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverlayIconButton({
    required IconData icon,
    Color iconColor = Colors.white,
    required String tooltip,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      shape: const CircleBorder(),
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: Container(
          width: 48.0,
          height: 48.0,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.black.withValues(alpha: 0.35),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.25),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Icon(
            icon,
            size: 22.0,
            color: iconColor,
          ),
        ),
      ),
    );
  }

  void _showInfoModal(BuildContext context, Wallpaper wallpaper) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        return DraggableScrollableSheet(
          initialChildSize: 0.65,
          minChildSize: 0.35,
          maxChildSize: 0.90,
          builder: (context, scrollController) {
            final theme = Theme.of(context);
            return Container(
              decoration: BoxDecoration(
                color: theme.scaffoldBackgroundColor,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(AppSizes.radiusLg),
                ),
              ),
              child: SingleChildScrollView(
                controller: scrollController,
                padding: const EdgeInsets.all(AppSizes.p20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Center(
                      child: Container(
                        width: 40.0,
                        height: 4.0,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.onSurfaceVariant
                              .withValues(alpha: 0.3),
                          borderRadius: BorderRadius.circular(2.0),
                        ),
                      ),
                    ),
                    const SizedBox(height: AppSizes.p16),
                    WallpaperMetadataCard(wallpaper: wallpaper),
                    const SizedBox(height: AppSizes.p16),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              AddToCollectionSheet.show(context, wallpaper);
                            },
                            icon: const Icon(Icons.bookmark_add_outlined),
                            label: const Text('Add to Collection'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: AppSizes.p20),
                    SimilarWallpapersSection(wallpaper: wallpaper),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Future<void> _handleDownload(
      BuildContext context, WidgetRef ref, Wallpaper wallpaper) async {
    final activeDownloads = ref.read(activeDownloadsProvider);
    if (activeDownloads.contains(wallpaper.id)) return;

    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Save to Gallery',
      message:
          'Wallpaper Gallery needs permission to save "${wallpaper.title}" to your device photo gallery.',
      confirmLabel: 'Grant & Download',
      cancelLabel: 'Cancel',
    );

    if (confirmed != true) return;

    if (!context.mounted) return;

    final result = await downloadWallpaper(ref, wallpaper);

    if (!context.mounted) return;

    final message = switch (result) {
      DownloadResult.success => 'Wallpaper "${wallpaper.title}" saved to Gallery',
      DownloadResult.permissionDenied =>
        'Storage permission required to save wallpaper',
      DownloadResult.error =>
        'Unable to save wallpaper. Please check permissions in device Settings.',
    };

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
}
