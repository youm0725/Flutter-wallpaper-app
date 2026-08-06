import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';

/// Reusable, refined non-interactive search bar UI component.
class SearchBarWidget extends StatelessWidget {
  final VoidCallback? onTap;
  final String hintText;

  const SearchBarWidget({
    super.key,
    this.onTap,
    this.hintText = 'Search wallpapers...',
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    final backgroundColor = isDark
        ? theme.colorScheme.surfaceContainerHighest
        : theme.colorScheme.surface;

    final borderColor = theme.colorScheme.outline.withValues(alpha: 0.3);

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSizes.p16),
      child: Material(
        color: backgroundColor,
        borderRadius: BorderRadius.circular(AppSizes.radiusMd),
        elevation: 0,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(AppSizes.radiusMd),
          child: Container(
            height: 48.0,
            padding: const EdgeInsets.symmetric(horizontal: AppSizes.p16),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(AppSizes.radiusMd),
              border: Border.all(
                color: borderColor,
                width: 1.0,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.search_rounded,
                  size: AppSizes.iconMd - 2,
                  color: theme.colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: AppSizes.p12),
                Expanded(
                  child: Text(
                    hintText,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.8),
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.all(AppSizes.p4),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                    borderRadius: BorderRadius.circular(AppSizes.radiusSm - 2),
                  ),
                  child: Icon(
                    Icons.tune_rounded,
                    size: AppSizes.iconSm,
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
