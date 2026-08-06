import 'package:flutter/foundation.dart';

/// Grid density preferences controlling wallpaper grid cross axis count.
enum GridDensity {
  compact,
  comfortable,
  large,
}

/// Immutable model storing user preferences and personalization settings.
@immutable
final class UserPreferences {
  final String themeMode;
  final GridDensity gridDensity;
  final bool showDailyWallpaper;
  final bool showFeaturedSection;
  final bool showRecentlyViewed;
  final bool showCollectionsSection;

  const UserPreferences({
    this.themeMode = 'system',
    this.gridDensity = GridDensity.comfortable,
    this.showDailyWallpaper = true,
    this.showFeaturedSection = true,
    this.showRecentlyViewed = true,
    this.showCollectionsSection = true,
  });

  /// Factory constructor to deserialize [UserPreferences] from a JSON map.
  factory UserPreferences.fromJson(Map<String, dynamic> json) {
    GridDensity density = GridDensity.comfortable;
    final densityStr = json['gridDensity'] as String?;
    if (densityStr == 'compact') {
      density = GridDensity.compact;
    } else if (densityStr == 'large') {
      density = GridDensity.large;
    }

    return UserPreferences(
      themeMode: json['themeMode'] as String? ?? 'system',
      gridDensity: density,
      showDailyWallpaper: json['showDailyWallpaper'] as bool? ?? true,
      showFeaturedSection: json['showFeaturedSection'] as bool? ?? true,
      showRecentlyViewed: json['showRecentlyViewed'] as bool? ?? true,
      showCollectionsSection: json['showCollectionsSection'] as bool? ?? true,
    );
  }

  /// Serializes this [UserPreferences] into a JSON map.
  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'themeMode': themeMode,
      'gridDensity': gridDensity.name,
      'showDailyWallpaper': showDailyWallpaper,
      'showFeaturedSection': showFeaturedSection,
      'showRecentlyViewed': showRecentlyViewed,
      'showCollectionsSection': showCollectionsSection,
    };
  }

  /// Returns a copy of [UserPreferences] with updated properties.
  UserPreferences copyWith({
    String? themeMode,
    GridDensity? gridDensity,
    bool? showDailyWallpaper,
    bool? showFeaturedSection,
    bool? showRecentlyViewed,
    bool? showCollectionsSection,
  }) {
    return UserPreferences(
      themeMode: themeMode ?? this.themeMode,
      gridDensity: gridDensity ?? this.gridDensity,
      showDailyWallpaper: showDailyWallpaper ?? this.showDailyWallpaper,
      showFeaturedSection: showFeaturedSection ?? this.showFeaturedSection,
      showRecentlyViewed: showRecentlyViewed ?? this.showRecentlyViewed,
      showCollectionsSection:
          showCollectionsSection ?? this.showCollectionsSection,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserPreferences &&
        other.themeMode == themeMode &&
        other.gridDensity == gridDensity &&
        other.showDailyWallpaper == showDailyWallpaper &&
        other.showFeaturedSection == showFeaturedSection &&
        other.showRecentlyViewed == showRecentlyViewed &&
        other.showCollectionsSection == showCollectionsSection;
  }

  @override
  int get hashCode {
    return Object.hash(
      themeMode,
      gridDensity,
      showDailyWallpaper,
      showFeaturedSection,
      showRecentlyViewed,
      showCollectionsSection,
    );
  }
}
