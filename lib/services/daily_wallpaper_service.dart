import '../models/wallpaper.dart';

/// Pure service providing 100% offline Wallpaper of the Day selection based on date hashing.
abstract interface class IDailyWallpaperService {
  Wallpaper? getDailyWallpaper(List<Wallpaper> wallpapers, {DateTime? date});
}

/// Production implementation of [IDailyWallpaperService].
final class DailyWallpaperService implements IDailyWallpaperService {
  const DailyWallpaperService();

  @override
  Wallpaper? getDailyWallpaper(List<Wallpaper> wallpapers, {DateTime? date}) {
    if (wallpapers.isEmpty) return null;

    final targetDate = date ?? DateTime.now();
    final dateHash = targetDate.year * 10000 + targetDate.month * 100 + targetDate.day;
    final selectedIndex = dateHash % wallpapers.length;

    return wallpapers[selectedIndex];
  }
}
