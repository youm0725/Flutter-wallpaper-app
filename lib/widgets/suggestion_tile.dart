import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../providers/search_providers.dart';

/// Reusable autocomplete suggestion item tile.
class SuggestionTile extends StatelessWidget {
  final SearchSuggestion suggestion;
  final VoidCallback onTap;

  const SuggestionTile({
    super.key,
    required this.suggestion,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    IconData icon;
    switch (suggestion.type) {
      case SuggestionType.category:
        icon = Icons.category_outlined;
        break;
      case SuggestionType.tag:
        icon = Icons.tag_rounded;
        break;
      case SuggestionType.wallpaper:
        icon = Icons.image_outlined;
        break;
    }

    return ListTile(
      onTap: onTap,
      leading: CircleAvatar(
        radius: 16.0,
        backgroundColor: theme.colorScheme.surfaceContainerHighest,
        child: Icon(
          icon,
          size: AppSizes.iconSm,
          color: theme.colorScheme.primary,
        ),
      ),
      title: Text(
        suggestion.title,
        style: theme.textTheme.bodyMedium?.copyWith(
          fontWeight: FontWeight.w600,
        ),
      ),
      subtitle: Text(
        suggestion.subtitle,
        style: theme.textTheme.bodySmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
      trailing: Icon(
        Icons.north_west_rounded,
        size: AppSizes.iconSm,
        color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.5),
      ),
    );
  }
}
