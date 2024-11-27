//
//  AppDelegate.m
//  Pythonista3AppTemplate
//
//  Created by Ole Zorn on 25.08.18.
//  Copyright © 2018 Ole Zorn. All rights reserved.
//

#import "PYAAppDelegate.h"
#import "PYAViewController.h"

#import <Py3Kit/Py3Kit.h>
#import <Py3Kit/PYKConstants.h>

@interface PYAAppDelegate ()

@end

@implementation PYAAppDelegate


- (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions
{
	NSDictionary *defaults = @{kPYKStandaloneMode: @(YES)};
	[[NSUserDefaults standardUserDefaults] registerDefaults:defaults];
	
	self.window = [[UIWindow alloc] initWithFrame:[[UIScreen mainScreen] bounds]];
	UIViewController *vc = [[PYAViewController alloc] init];
	self.window.backgroundColor = [UIColor colorNamed:@"Color"];
	self.window.rootViewController = vc;
	[self.window makeKeyAndVisible];
	[self copyScriptResourcesIfNeeded];
	[self runScript];
	return YES;
}

- (NSString *)documentsDirectory
{
	return [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
}

- (void)copyScriptResourcesIfNeeded
{
	// Copy the script and any resource files it needs to a writable directory in the app's sandbox.
	// While it would technically be possible to run script directly out of the app bundle, this
	// can lead to unexpected behavior compared to running scripts in Pythonista.
	// In order to support editing the script in Xcode, the app checks if the files are up-to-date
	// on every launch.
	NSFileManager *fm = [NSFileManager defaultManager];
	NSString *bundledScriptDirectoryPath = [[[NSBundle mainBundle] resourcePath] stringByAppendingPathComponent:@"outfit_saver"];
	NSString *docPath = [self documentsDirectory];
    // Copy over src files
	NSString *fromSrcPath = [bundledScriptDirectoryPath stringByAppendingPathComponent:@"src"];
	NSString *toSrcPath = [docPath stringByAppendingPathComponent:@"src"];
	NSError *error;
	if ([fm createDirectoryAtPath:toSrcPath
								  withIntermediateDirectories:YES
												   attributes:nil
														error:&error]) {
		NSLog(@"Directory created successfully: %@", toSrcPath);
	} else {
		NSLog(@"Error creating directory: %@", error);
	}
	NSArray *contents = [fm contentsOfDirectoryAtPath:fromSrcPath error:NULL];
	for (NSString *filename in contents) {
		NSLog(@"found file: %@", filename);
		NSString *srcPath = [fromSrcPath stringByAppendingPathComponent:filename];
		NSString *destPath = [toSrcPath stringByAppendingPathComponent:filename];
		BOOL changed = NO;
		if (![fm fileExistsAtPath:destPath]) {
			changed = YES;
		} else {
			NSDate *srcDate = [[fm attributesOfItemAtPath:srcPath error:NULL] fileModificationDate];
			NSDate *destDate = [[fm attributesOfItemAtPath:destPath error:NULL] fileModificationDate];
			changed = ![srcDate isEqualToDate:destDate];
		}
		if (changed) {
			NSLog(@"changing: %@", filename);
			[fm removeItemAtPath:destPath error:NULL];
			[fm copyItemAtPath:srcPath toPath:destPath error:NULL];
		}
	}
	// Copy over button_images files
	NSString *fromImagePath = [bundledScriptDirectoryPath stringByAppendingPathComponent:@"images/button_images"];
	NSString *toImagePath = [docPath stringByAppendingPathComponent:@"images/button_images"];
	if ([fm createDirectoryAtPath:toImagePath
								  withIntermediateDirectories:YES
												   attributes:nil
														error:&error]) {
		NSLog(@"Directory created successfully: %@", toImagePath);
	} else {
		NSLog(@"Error creating directory: %@", error);
	}
	contents = [fm contentsOfDirectoryAtPath:fromImagePath error:NULL];
	for (NSString *filename in contents) {
		NSLog(@"found file: %@", filename);
		NSString *srcPath = [fromImagePath stringByAppendingPathComponent:filename];
		NSString *destPath = [toImagePath stringByAppendingPathComponent:filename];
		BOOL changed = NO;
		if (![fm fileExistsAtPath:destPath]) {
			changed = YES;
		} else {
			NSDate *srcDate = [[fm attributesOfItemAtPath:srcPath error:NULL] fileModificationDate];
			NSDate *destDate = [[fm attributesOfItemAtPath:destPath error:NULL] fileModificationDate];
			changed = ![srcDate isEqualToDate:destDate];
		}
		if (changed) {
			NSLog(@"changing: %@", filename);
			[fm removeItemAtPath:destPath error:NULL];
			[fm copyItemAtPath:srcPath toPath:destPath error:NULL];
		}
	}
}

- (void)runScript
{
	// If the main entry point of your script is not main.py, you can change the filename here.
	NSString *scriptFilename = @"src/outfit_saver.py";
	NSString *scriptPath = [[self documentsDirectory] stringByAppendingPathComponent:scriptFilename];
	if (![[NSFileManager defaultManager] fileExistsAtPath:scriptPath]) {
		NSLog(@"Error: src/outfit_saver.py not found.");
		return;
	}
	[[PYK3Interpreter sharedInterpreter] runScriptAtPath:scriptPath argv:nil resetEnvironment:YES];
}

@end
