import 'package:flutter/foundation.dart';

/// Strongly-typed domain model for wallpaper categories.
@immutable
class Category {
  final String id;
  final String name;
  final String description;
  final int wallpaperCount;
  final String? previewImagePath;
  final String iconName;

  const Category({
    required this.id,
    required this.name,
    this.description = '',
    this.wallpaperCount = 0,
    this.previewImagePath,
    this.iconName = 'category',
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    final rawId = (json['id'] as String? ?? '').trim();
    final rawName = (json['name'] as String? ?? '').trim();
    return Category(
      id: rawId.toLowerCase(),
      name: rawName.isNotEmpty ? rawName : rawId.toUpperCase(),
      description: (json['description'] as String? ?? '').trim(),
      iconName: (json['icon'] as String? ?? json['iconName'] as String? ?? 'category').trim(),
    );
  }

  Category copyWith({
    String? id,
    String? name,
    int? wallpaperCount,
    String? previewImagePath,
    String? iconName,
  }) {
    return Category(
      id: id ?? this.id,
      name: name ?? this.name,
      wallpaperCount: wallpaperCount ?? this.wallpaperCount,
      previewImagePath: previewImagePath ?? this.previewImagePath,
      iconName: iconName ?? this.iconName,
    );
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Category &&
        other.id == id &&
        other.name == name &&
        other.wallpaperCount == wallpaperCount &&
        other.previewImagePath == previewImagePath &&
        other.iconName == iconName;
  }

  @override
  int get hashCode {
    return Object.hash(
      id,
      name,
      wallpaperCount,
      previewImagePath,
      iconName,
    );
  }

  @override
  String toString() {
    return 'Category(id: $id, name: $name, count: $wallpaperCount)';
  }
}
