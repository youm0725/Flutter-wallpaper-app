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

  const UserPreferences({
    this.themeMode = 'system',
    this.gridDensity = GridDensity.comfortable,
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
    );
  }

  /// Serializes this [UserPreferences] into a JSON map.
  Map<String, dynamic> toJson() {
    return <String, dynamic>{
      'themeMode': themeMode,
      'gridDensity': gridDensity.name,
    };
  }

  /// Returns a copy of [UserPreferences] with updated properties.
  UserPreferences copyWith({
    String? themeMode,
    GridDensity? gridDensity,
  }) {
    return UserPreferences(
      themeMode: themeMode ?? this.themeMode,
      gridDensity: gridDensity ?? this.gridDensity,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is UserPreferences &&
        other.themeMode == themeMode &&
        other.gridDensity == gridDensity;
  }

  @override
  int get hashCode {
    return Object.hash(
      themeMode,
      gridDensity,
    );
  }
}
