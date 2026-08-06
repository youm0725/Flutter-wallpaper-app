import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../providers/favorites_provider.dart';
import '../../providers/preferences_provider.dart';
import '../../providers/recently_viewed_provider.dart';
import '../../providers/share_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/user_collection_provider.dart';
import '../../widgets/widgets.dart';

/// Full Settings Screen — Appearance, Grid Layout, Home Feed, Data Management,
/// About & Share, and Backup & Restore sections.
class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  static const int _currentBottomNavIndex = 2;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncPrefs = ref.watch(userPreferencesNotifierProvider);
    final asyncTheme = ref.watch(themeModeProvider);
    final currentThemeMode = asyncTheme.value ?? ThemeMode.system;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SafeArea(
        child: asyncPrefs.when(
          data: (prefs) => ListView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(vertical: AppSizes.p12),
            children: [

              // ── 1. APPEARANCE ──────────────────────────────────────────
              const SectionHeader(
                title: 'Appearance',
                subtitle: 'Theme and layout preferences',
              ),

              // Theme mode: System / Light / Dark
              PreferenceTile(
                icon: Icons.brightness_auto_rounded,
                title: 'App Theme',
                subtitle: _themeModeLabel(currentThemeMode),
                trailing: ThemeSelector(
                  selectedMode: currentThemeMode,
                  onSelected: (mode) =>
                      ref.read(themeModeProvider.notifier).setThemeMode(mode),
                ),
              ),

              // Grid density
              PreferenceTile(
                icon: Icons.grid_view_rounded,
                title: 'Wallpaper Grid Layout',
                subtitle: 'Control thumbnail density',
                trailing: OptionSelector(
                  selectedDensity: prefs.gridDensity,
                  onSelected: (density) => ref
                      .read(userPreferencesNotifierProvider.notifier)
                      .setGridDensity(density),
                ),
              ),

              const Divider(height: AppSizes.p32),

              // ── 2. HOME FEED ────────────────────────────────────────────
              const SectionHeader(
                title: 'Home Feed',
                subtitle: 'Toggle discovery sections',
              ),
              PreferenceTile(
                icon: Icons.today_rounded,
                title: 'Wallpaper of the Day',
                subtitle: 'Daily hero banner',
                trailing: Switch.adaptive(
                  value: prefs.showDailyWallpaper,
                  onChanged: (val) => ref
                      .read(userPreferencesNotifierProvider.notifier)
                      .toggleDailyWallpaper(val),
                ),
              ),
              PreferenceTile(
                icon: Icons.star_outline_rounded,
                title: "Editor's Picks",
                subtitle: 'Featured wallpapers section',
                trailing: Switch.adaptive(
                  value: prefs.showFeaturedSection,
                  onChanged: (val) => ref
                      .read(userPreferencesNotifierProvider.notifier)
                      .toggleFeaturedSection(val),
                ),
              ),
              PreferenceTile(
                icon: Icons.history_rounded,
                title: 'Recently Viewed',
                subtitle: 'Recent view history section',
                trailing: Switch.adaptive(
                  value: prefs.showRecentlyViewed,
                  onChanged: (val) => ref
                      .read(userPreferencesNotifierProvider.notifier)
                      .toggleRecentlyViewed(val),
                ),
              ),
              PreferenceTile(
                icon: Icons.collections_bookmark_outlined,
                title: 'Curated Collections',
                subtitle: 'Themed collections on home feed',
                trailing: Switch.adaptive(
                  value: prefs.showCollectionsSection,
                  onChanged: (val) => ref
                      .read(userPreferencesNotifierProvider.notifier)
                      .toggleCollectionsSection(val),
                ),
              ),

              const Divider(height: AppSizes.p32),

              // ── 3. DATA MANAGEMENT ──────────────────────────────────────
              const SectionHeader(
                title: 'Data & Library',
                subtitle: 'Manage local offline data',
              ),
              PreferenceTile(
                icon: Icons.folder_special_outlined,
                title: 'Personal Collections',
                subtitle: 'Manage custom wallpaper libraries',
                trailing: const Icon(Icons.chevron_right_rounded),
                onTap: () =>
                    context.pushNamed(RouteConstants.userCollectionsName),
              ),
              PreferenceTile(
                icon: Icons.delete_outline_rounded,
                title: 'Clear Recently Viewed',
                subtitle: 'Reset wallpaper view history',
                onTap: () => _clearRecentlyViewed(context, ref),
              ),
              PreferenceTile(
                icon: Icons.heart_broken_outlined,
                title: 'Clear All Favorites',
                subtitle: 'Remove all saved wallpapers',
                onTap: () => _clearFavorites(context, ref),
              ),
              PreferenceTile(
                icon: Icons.folder_delete_outlined,
                title: 'Delete All Collections',
                subtitle: 'Remove all personal wallpaper libraries',
                onTap: () => _deleteAllCollections(context, ref),
              ),

              const Divider(height: AppSizes.p32),

              // ── 4. ABOUT & SHARE ────────────────────────────────────────
              const SectionHeader(
                title: 'About & Share',
                subtitle: 'Share the app with friends',
              ),
              PreferenceTile(
                icon: Icons.info_outline_rounded,
                title: 'About Wallpaper Gallery',
                subtitle: 'Version, privacy, licenses & support',
                trailing: const Icon(Icons.chevron_right_rounded),
                onTap: () => context.pushNamed(RouteConstants.aboutName),
              ),
              PreferenceTile(
                icon: Icons.share_rounded,
                title: 'Share Wallpaper Gallery',
                subtitle: 'Spread the word',
                onTap: () => shareApp(ref),
              ),

              const Divider(height: AppSizes.p32),

              // ── 5. BACKUP & RESTORE ─────────────────────────────────────
              const SectionHeader(
                title: 'Backup & Restore',
                subtitle: 'Offline data management',
              ),
              PreferenceTile(
                icon: Icons.upload_file_outlined,
                title: 'Export Local Backup',
                subtitle: 'Generate offline JSON snapshot',
                onTap: () => _exportBackup(context, ref, prefs),
              ),
              PreferenceTile(
                icon: Icons.restore_page_outlined,
                title: 'Reset All Preferences',
                subtitle: 'Restore default settings',
                onTap: () => _resetPreferences(context, ref),
              ),

              const SizedBox(height: AppSizes.p32),
            ],
          ),
          loading: () => const LoadingView(message: 'Loading settings...'),
          error: (error, _) => ErrorStateView(message: error.toString()),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentBottomNavIndex,
        onTap: (index) => _onBottomNavTapped(context, index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.favorite_outline_rounded),
            activeIcon: Icon(Icons.favorite_rounded),
            label: 'Favorites',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings_rounded),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  // ── Helpers ──────────────────────────────────────────────────────────────

  String _themeModeLabel(ThemeMode mode) {
    switch (mode) {
      case ThemeMode.system:
        return 'Follow system setting';
      case ThemeMode.light:
        return 'Light theme';
      case ThemeMode.dark:
        return 'Dark theme';
    }
  }

  void _onBottomNavTapped(BuildContext context, int index) {
    if (index == _currentBottomNavIndex) return;
    if (index == 0) context.goNamed(RouteConstants.homeName);
    if (index == 1) context.goNamed(RouteConstants.favoritesName);
  }

  Future<void> _clearRecentlyViewed(
      BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Clear History?',
      message: 'This will remove all wallpapers from your recently viewed list.',
      confirmLabel: 'Clear',
      isDestructive: true,
    );
    if (confirmed == true) {
      await ref
          .read(recentlyViewedNotifierProvider.notifier)
          .clearHistory();
      if (context.mounted) {
        _showSnackBar(context, 'Recently viewed history cleared');
      }
    }
  }

  Future<void> _clearFavorites(BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Clear Favorites?',
      message: 'All saved favorite wallpapers will be removed.',
      confirmLabel: 'Clear All',
      isDestructive: true,
    );
    if (confirmed == true) {
      await ref.read(favoritesRepositoryProvider).clearFavorites();
      ref.invalidate(favoritesNotifierProvider);
      if (context.mounted) {
        _showSnackBar(context, 'Favorites cleared');
      }
    }
  }

  Future<void> _deleteAllCollections(
      BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Delete All Collections?',
      message:
          'All personal wallpaper libraries will be permanently deleted. This cannot be undone.',
      confirmLabel: 'Delete All',
      isDestructive: true,
    );
    if (confirmed == true) {
      final collections =
          ref.read(userCollectionsNotifierProvider).value ?? [];
      for (final col in collections) {
        await ref
            .read(userCollectionsNotifierProvider.notifier)
            .deleteCollection(col.id);
      }
      if (context.mounted) {
        _showSnackBar(context, 'All collections deleted');
      }
    }
  }

  Future<void> _exportBackup(
      BuildContext context, WidgetRef ref, dynamic prefs) async {
    final favs =
        ref.read(favoritesNotifierProvider).value?.toList() ?? [];
    final userCols = ref
            .read(userCollectionsNotifierProvider)
            .value
            ?.map((c) => c.toJson())
            .toList() ??
        [];
    final currentPrefs = (prefs as dynamic).toJson() as Map<String, dynamic>;

    final backupService = ref.read(backupServiceProvider);
    final jsonStr = await backupService.exportBackupToJson(
      favorites: favs,
      userCollections: userCols,
      preferences: currentPrefs,
    );

    if (context.mounted) {
      showDialog<void>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Backup Exported'),
          content: SingleChildScrollView(
            child: SelectableText(
              jsonStr,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 12.0),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Close'),
            ),
          ],
        ),
      );
    }
  }

  Future<void> _resetPreferences(
      BuildContext context, WidgetRef ref) async {
    final confirmed = await ConfirmationDialog.show(
      context,
      title: 'Reset Preferences?',
      message: 'All layout and view preferences will be restored to default.',
      confirmLabel: 'Reset',
    );
    if (confirmed == true) {
      await ref
          .read(userPreferencesNotifierProvider.notifier)
          .resetAll();
      if (context.mounted) {
        _showSnackBar(context, 'Preferences reset to default');
      }
    }
  }

  void _showSnackBar(BuildContext context, String message) {
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
}
