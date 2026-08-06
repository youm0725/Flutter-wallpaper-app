import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';

/// Reusable loading indicator view widget.
class LoadingView extends StatelessWidget {
  final String? message;

  const LoadingView({
    super.key,
    this.message = 'Loading wallpapers...',
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppSizes.p24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(
              strokeWidth: 3.0,
            ),
            if (message != null) ...[
              const SizedBox(height: AppSizes.p16),
              Text(
                message!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
