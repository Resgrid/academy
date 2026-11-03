import type { VariantProps } from '@gluestack-ui/utils/nativewind-utils';
import React from 'react';
import type { TextProps as NativeTextProps } from 'react-native';

import { toDomProps } from '@/components/ui/utils/dom-props';

import { textStyle } from './styles';

type ITextProps = Omit<React.ComponentProps<'span'>, 'style'> &
  VariantProps<typeof textStyle> &
  Pick<NativeTextProps, 'onPress' | 'accessibilityRole' | 'accessibilityLabel' | 'accessibilityHint' | 'accessibilityState' | 'accessibilityValue'> & {
    style?: React.CSSProperties | NativeTextProps['style'];
    numberOfLines?: number;
    ellipsizeMode?: 'head' | 'middle' | 'tail' | 'clip';
    testID?: string;
  };

const Text = React.forwardRef<React.ElementRef<'span'>, ITextProps>(
  ({ className, isTruncated, bold, underline, strikeThrough, size = 'md', sub, italic, highlight, numberOfLines, ellipsizeMode: _ellipsizeMode, testID, style, ...props }: { className?: string } & ITextProps, ref) => {
    const lineClampStyle: React.CSSProperties | undefined = numberOfLines
      ? {
          display: '-webkit-box',
          WebkitBoxOrient: 'vertical',
          WebkitLineClamp: numberOfLines,
          overflow: 'hidden',
        }
      : undefined;

    return (
      <span
        className={textStyle({
          isTruncated,
          bold,
          underline,
          strikeThrough,
          size,
          sub,
          italic,
          highlight,
          class: className,
        })}
        {...toDomProps({ ...props, testID, style: [lineClampStyle, style] })}
        ref={ref}
      />
    );
  }
);

Text.displayName = 'Text';

export { Text };
