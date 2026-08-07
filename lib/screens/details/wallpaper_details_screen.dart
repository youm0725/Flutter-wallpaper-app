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

/// Full-screen, edge-to-edge wallpaper viewer with PageView swiping, left/right scroll arrows, top-left back button & animated bottom-left expandable action menu.
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
    extends ConsumerState<WallpaperDetailsScreen>
    with SingleTickerProviderStateMixin {
  bool _showControls = true;
  bool _isFabExpanded = false;
  late AnimationController _fabAnimationController;
  late Animation<double> _expandAnimation;
  late Animation<double> _rotationAnimation;

  PageController? _pageController;
  int _currentIndex = 0;
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _fabAnimationController = AnimationController(
      value: 0.0,
      duration: const Duration(milliseconds: 250),
      vsync: this,
    );
    _expandAnimation = CurvedAnimation(
      parent: _fabAnimationController,
      curve: Curves.easeOutBack,
      reverseCurve: Curves.easeIn,
    );
    _rotationAnimation = Tween<double>(begin: 0.0, end: 0.125).animate(
      CurvedAnimation(
        parent: _fabAnimationController,
        curve: Curves.easeInOut,
      ),
    );
  }

  @override
  void dispose() {
    _fabAnimationController.dispose();
    _pageController?.dispose();
    super.dispose();
  }

  void _toggleControls() {
    setState(() {
      _showControls = !_showControls;
      if (!_showControls && _isFabExpanded) {
        _isFabExpanded = false;
        _fabAnimationController.reverse();
      }
    });
  }

  void _toggleFabMenu() {
    setState(() {
      _isFabExpanded = !_isFabExpanded;
      if (_isFabExpanded) {
        _fabAnimationController.forward();
      } else {
        _fabAnimationController.reverse();
      }
    });
  }

  void _initPageController(List<Wallpaper> wallpapers) {
    if (_isInitialized) return;

    int initialIndex = wallpapers.indexWhere((w) => w.id == widget.wallpaperId);
    if (initialIndex < 0) initialIndex = 0;

    _currentIndex = initialIndex;
    _pageController = PageController(initialPage: initialIndex);
    _isInitialized = true;
  }

  @override
  Widget build(BuildContext context) {
    final asyncWallpapers = ref.watch(wallpapersProvider);

    return asyncWallpapers.when(
      data: (wallpapers) {
        if (wallpapers.isEmpty && widget.wallpaper != null) {
          return _buildFullscreenViewer(context, [widget.wallpaper!]);
        }
        if (wallpapers.isEmpty) {
          return Scaffold(
            backgroundColor: Colors.black,
            appBar: AppBar(backgroundColor: Colors.black),
            body: const EmptyStateView(
              title: 'No Wallpapers',
              description: 'Unable to load wallpaper gallery.',
            ),
          );
        }

        _initPageController(wallpapers);
        return _buildFullscreenViewer(context, wallpapers);
      },
      loading: () => Scaffold(
        backgroundColor: Colors.black,
        body: widget.wallpaper != null
            ? _buildFullscreenViewer(context, [widget.wallpaper!])
            : const LoadingView(message: 'Loading full wallpaper...'),
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

  Widget _buildFullscreenViewer(BuildContext context, List<Wallpaper> wallpapers) {
    final currentWallpaper = wallpapers[_currentIndex < wallpapers.length ? _currentIndex : 0];
    final asyncFavIds = ref.watch(favoritesNotifierProvider);
    final isFav = asyncFavIds.value?.contains(currentWallpaper.id) ?? false;
    final activeDownloads = ref.watch(activeDownloadsProvider);
    final isDownloading = activeDownloads.contains(currentWallpaper.id);

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
            // 1. Full-screen Swipeable PageView Wallpaper Viewer
            PageView.builder(
              controller: _pageController,
              itemCount: wallpapers.length,
              onPageChanged: (index) {
                setState(() {
                  _currentIndex = index;
                  if (_isFabExpanded) {
                    _isFabExpanded = false;
                    _fabAnimationController.reverse();
                  }
                });
              },
              itemBuilder: (context, index) {
                final wallpaper = wallpapers[index];
                return ZoomableWallpaper(
                  wallpaper: wallpaper,
                  height: double.infinity,
                  onTap: _toggleControls,
                );
              },
            ),

            // 2. Top-Left Floating Back Button
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
                      padding: const EdgeInsets.only(
                        left: AppSizes.p16,
                        top: AppSizes.p12,
                      ),
                      child: Material(
                        color: Colors.black.withValues(alpha: 0.45),
                        shape: const CircleBorder(),
                        child: InkWell(
                          customBorder: const CircleBorder(),
                          onTap: () => context.pop(),
                          child: const Padding(
                            padding: EdgeInsets.all(AppSizes.p12),
                            child: Icon(
                              Icons.arrow_back_rounded,
                              size: 24.0,
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

            // 3. Middle-Left Previous Wallpaper Scroll Arrow
            if (_showControls && _currentIndex > 0)
              Align(
                alignment: Alignment.centerLeft,
                child: Padding(
                  padding: const EdgeInsets.only(left: AppSizes.p12),
                  child: Material(
                    color: Colors.black.withValues(alpha: 0.45),
                    shape: const CircleBorder(),
                    child: InkWell(
                      customBorder: const CircleBorder(),
                      onTap: () {
                        _pageController?.previousPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      },
                      child: const Padding(
                        padding: EdgeInsets.all(AppSizes.p12),
                        child: Icon(
                          Icons.chevron_left_rounded,
                          size: 32.0,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ),
              ),

            // 4. Middle-Right Next Wallpaper Scroll Arrow
            if (_showControls && _currentIndex < wallpapers.length - 1)
              Align(
                alignment: Alignment.centerRight,
                child: Padding(
                  padding: const EdgeInsets.only(right: AppSizes.p12),
                  child: Material(
                    color: Colors.black.withValues(alpha: 0.45),
                    shape: const CircleBorder(),
                    child: InkWell(
                      customBorder: const CircleBorder(),
                      onTap: () {
                        _pageController?.nextPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      },
                      child: const Padding(
                        padding: EdgeInsets.all(AppSizes.p12),
                        child: Icon(
                          Icons.chevron_right_rounded,
                          size: 32.0,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                ),
              ),

            // 5. Bottom-Left Expandable Plus (+) Action Menu
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
                    alignment: Alignment.bottomLeft,
                    child: Padding(
                      padding: const EdgeInsets.only(
                        left: AppSizes.p20,
                        bottom: AppSizes.p20,
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Expanded Action Buttons Menu
                          SizeTransition(
                            sizeFactor: _expandAnimation,
                            alignment: Alignment.bottomLeft,
                            child: FadeTransition(
                              opacity: _expandAnimation,
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // 1. Details Button
                                  _buildFabMenuItem(
                                    icon: Icons.info_outline_rounded,
                                    label: 'Details',
                                    onTap: () {
                                      _toggleFabMenu();
                                      _showInfoModal(context, currentWallpaper);
                                    },
                                  ),
                                  const SizedBox(height: AppSizes.p12),

                                  // 2. Favorite Button
                                  _buildFabMenuItem(
                                    icon: isFav
                                        ? Icons.favorite_rounded
                                        : Icons.favorite_outline_rounded,
                                    iconColor:
                                        isFav ? Colors.redAccent : Colors.white,
                                    label: isFav
                                        ? 'Remove Favorite'
                                        : 'Favorite',
                                    onTap: () {
                                      ref
                                          .read(
                                              favoritesNotifierProvider.notifier)
                                          .toggleFavorite(currentWallpaper.id);
                                    },
                                  ),
                                  const SizedBox(height: AppSizes.p12),

                                  // 3. Download Button
                                  _buildFabMenuItem(
                                    icon: isDownloading
                                        ? Icons.hourglass_top_rounded
                                        : Icons.save_outlined,
                                    label: 'Save to Gallery',
                                    onTap: () {
                                      _toggleFabMenu();
                                      _handleDownload(context, ref, currentWallpaper);
                                    },
                                  ),
                                  const SizedBox(height: AppSizes.p12),

                                  // 4. Set Wallpaper Button
                                  _buildFabMenuItem(
                                    icon: Icons.shortcut_rounded,
                                    label: 'Set Wallpaper',
                                    onTap: () {
                                      _toggleFabMenu();
                                      SetWallpaperSheet.show(
                                          context, currentWallpaper);
                                    },
                                  ),
                                  const SizedBox(height: AppSizes.p16),
                                ],
                              ),
                            ),
                          ),

                          // Main Plus (+) Button
                          RotationTransition(
                            turns: _rotationAnimation,
                            child: Material(
                              color: Colors.transparent,
                              shape: const CircleBorder(),
                              child: InkWell(
                                customBorder: const CircleBorder(),
                                onTap: _toggleFabMenu,
                                child: Container(
                                  width: 56.0,
                                  height: 56.0,
                                  alignment: Alignment.center,
                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: Colors.black.withValues(alpha: 0.75),
                                    border: Border.all(
                                      color: Colors.white.withValues(alpha: 0.30),
                                      width: 1.5,
                                    ),
                                    boxShadow: [
                                      BoxShadow(
                                        color:
                                            Colors.black.withValues(alpha: 0.50),
                                        blurRadius: 10,
                                        offset: const Offset(0, 4),
                                      ),
                                    ],
                                  ),
                                  child: const Icon(
                                    Icons.add_rounded,
                                    size: 28.0,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                            ),
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

  Widget _buildFabMenuItem({
    required IconData icon,
    Color iconColor = Colors.white,
    required String label,
    required VoidCallback onTap,
  }) {
    return Material(
      color: Colors.transparent,
      borderRadius: BorderRadius.circular(30.0),
      child: InkWell(
        borderRadius: BorderRadius.circular(30.0),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSizes.p16,
            vertical: 10.0,
          ),
          decoration: BoxDecoration(
            color: Colors.black.withValues(alpha: 0.65),
            borderRadius: BorderRadius.circular(30.0),
            border: Border.all(
              color: Colors.white.withValues(alpha: 0.15),
            ),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.30),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                icon,
                size: 20.0,
                color: iconColor,
              ),
              const SizedBox(width: AppSizes.p8),
              Text(
                label,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 13.0,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
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
