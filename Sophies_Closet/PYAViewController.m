//
//  ViewController.m
//  Pythonista3AppTemplate
//
//  Created by Ole Zorn on 25.08.18.
//  Copyright © 2018 Ole Zorn. All rights reserved.
//

#import "PYAViewController.h"
#import <Py3Kit/Py3Kit.h>
#import <Py3Kit/PYKConstants.h>

@interface PYAViewController ()

@property (nonatomic, strong) UITextView *outputTextView;
@property (nonatomic, strong) UIFont *defaultOutputFont;

@end


@implementation PYAViewController

- (instancetype)init
{
	self = [super initWithNibName:nil bundle:nil];
	if (self) {
		
	}
	return self;
}

- (void)loadView
{
	[super loadView];
	self.view.backgroundColor = [UIColor clearColor];
	UIEdgeInsets insets = UIEdgeInsetsMake(20, 0, 0, 0);
	self.outputTextView = [[UITextView alloc] initWithFrame:UIEdgeInsetsInsetRect(self.view.bounds, insets)];
	self.outputTextView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
	self.outputTextView.editable = NO;
	self.outputTextView.backgroundColor = self.view.backgroundColor;
	self.defaultOutputFont = [UIFont fontWithName:@"Menlo" size:12.0];
	[self.view addSubview:self.outputTextView];
	
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(consoleTextOutput:) name:PYKIOTextOutputNotification object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(consoleTextOutput:) name:PYKIOErrorOutputNotification object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(consoleImageOutput:) name:@"ConsoleOutputImageNotification" object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(consoleClearOutput:) name:@"ClearOutputNotification" object:nil];
	[[NSNotificationCenter defaultCenter] addObserver:self selector:@selector(consoleTextInput:) name:PYKIOWaitingForTextInputNotification object:nil];
}

- (void)consoleTextOutput:(NSNotification *)notification
{
	dispatch_async(dispatch_get_main_queue(), ^{
		NSString *text = [notification.userInfo objectForKey:@"output"];
		NSMutableDictionary *textAttributes = [NSMutableDictionary dictionaryWithObject:self.defaultOutputFont forKey:NSFontAttributeName];
		UIColor *outputColor = [notification.name isEqualToString:PYKIOErrorOutputNotification] ? [UIColor colorWithRed:0.6706 green:0.3137 blue:0.2431 alpha:1.0] : [UIColor colorWithWhite:0.2 alpha:1.0];
		[textAttributes setObject:outputColor forKey:NSForegroundColorAttributeName];
		NSString *linkURLString = [notification.userInfo objectForKey:@"linkURL"];
		NSURL *linkURL = linkURLString ? [NSURL URLWithString:linkURLString] : nil;
		if (linkURL) {
			[textAttributes setObject:@(NSUnderlineStyleSingle) forKey:NSUnderlineStyleAttributeName];
			[textAttributes setObject:linkURL forKey:NSLinkAttributeName];
		}
		NSAttributedString *attributedText = [[NSAttributedString alloc] initWithString:text attributes:textAttributes];
		[self.outputTextView.textStorage appendAttributedString:attributedText];
		[UIView performWithoutAnimation:^{
			[self.outputTextView scrollRangeToVisible:NSMakeRange(self.outputTextView.text.length, 0)];
		}];
	});
}

- (void)consoleImageOutput:(NSNotification *)notification
{
	UIImage *image = [notification.userInfo objectForKey:@"image"];
	NSString *imagePath = [notification.userInfo objectForKey:@"imagePath"];
	if (!image && imagePath) {
		image = [UIImage imageWithContentsOfFile:imagePath];
	}
	if (!image) {
		return;
	}
	dispatch_async(dispatch_get_main_queue(), ^{
		NSTextAttachment *attachment = [[NSTextAttachment alloc] initWithData:nil ofType:nil];
		CGFloat maxWidth = self.view.bounds.size.width - 10.0;
		CGFloat scaleFactor = MIN(1.0, maxWidth / image.size.width);
		attachment.bounds = CGRectMake(0, 0, image.size.width * scaleFactor, image.size.height * scaleFactor);
		attachment.image = image;
		NSDictionary *attributes = @{NSFontAttributeName: self.defaultOutputFont};
		NSMutableAttributedString *attachmentString = [[NSMutableAttributedString alloc] initWithString:@"\n\ufffc\n" attributes:attributes];
		[attachmentString addAttribute:NSAttachmentAttributeName value:attachment range:NSMakeRange(1, 1)];
		[self.outputTextView.textStorage appendAttributedString:attachmentString];
	});
}

- (void)consoleClearOutput:(id)sender
{
	dispatch_async(dispatch_get_main_queue(), ^{
		[self.outputTextView setText:@""];
	});
}

- (void)consoleTextInput:(NSNotification *)notification
{
	UIAlertController *alert = [UIAlertController alertControllerWithTitle:@"Text Input" message:nil preferredStyle:UIAlertControllerStyleAlert];
	[alert addTextFieldWithConfigurationHandler:^(UITextField * _Nonnull textField) {
		textField.autocorrectionType = UITextAutocorrectionTypeNo;
		textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
		textField.spellCheckingType = UITextSpellCheckingTypeNo;
	}];
	__weak UIAlertController *weakAlert = alert;
	[alert addAction:[UIAlertAction actionWithTitle:@"OK" style:UIAlertActionStyleDefault handler:^(UIAlertAction * _Nonnull action) {
		UITextField *textField = [weakAlert.textFields firstObject];
		NSString *text = [textField.text stringByAppendingString:@"\n"];
		[[PYK3Interpreter sharedInterpreter] writeStdIn:text];
	}]];
	UIViewController *presentationViewController = self;
	while (presentationViewController.presentedViewController) {
		presentationViewController = presentationViewController.presentedViewController;
	}
	[presentationViewController presentViewController:alert animated:YES completion:nil];
}

- (void)dealloc
{
	[[NSNotificationCenter defaultCenter] removeObserver:self];
}

@end
