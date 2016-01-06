%global pkg_name glassfish-hk2
%{?scl:%scl_package %{pkg_name}}
%global namedreltag -b25
%global namedversion %{version}%{?namedreltag}

%{?java_common_find_provides_and_requires}
Name:          %{?scl_prefix}glassfish-hk2
Version:       2.4.0
Release:       0.7.3.b25%{?dist}
Summary:       Hundred Kilobytes Kernel
License:       CDDL or GPLv2 with exceptions
URL:           http://hk2.java.net/
Source0:       https://github.com/hk2-project/hk2/archive/hk2-parent-%{namedversion}.tar.gz
# https://java.net/jira/browse/HK2-250
# wget -O glassfish-LICENSE.txt https://svn.java.net/svn/glassfish~svn/tags/legal-1.1/src/main/resources/META-INF/LICENSE.txt
# glassfish-hk2 package don't include the license file
Source1:       glassfish-LICENSE.txt
Source2:       hk2-inhabitant-generator-osgi.bundle

Patch0:        glassfish-hk2-2.3.0-hk2-utils-osgi_bundle.patch
Patch1:        glassfish-hk2-2.4.0-b24-disable-asm-all-repackaged.patch
Patch2:        glassfish-hk2-2.3.0-disable-external-aopalliance.patch

BuildRequires: %{?scl_prefix_java_common}maven-local
BuildRequires: %{?scl_prefix}mvn(aopalliance:aopalliance)
BuildRequires: %{?scl_prefix_java_common}mvn(javax.inject:javax.inject)
BuildRequires: %{?scl_prefix_maven}mvn(net.java:jvnet-parent:pom:)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven:maven-plugin-api)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.plugins:maven-compiler-plugin)
BuildRequires: %{?scl_prefix_maven}mvn(org.apache.maven.shared:maven-osgi)
BuildRequires: %{?scl_prefix}mvn(org.glassfish.hk2:osgi-resource-locator)
BuildRequires: %{?scl_prefix}mvn(org.javassist:javassist)
BuildRequires: %{?scl_prefix}mvn(org.jvnet:tiger-types)

BuildArch:     noarch

%description
HK2 for Hundred Kilobytes Kernel is an abstraction to
a module subsystem coupled with a simple yet powerful
component model to build server side software.

%package api
Summary:       HK2 API module

%description api
Hundred Kilobytes Kernel API module.

%package locator
Summary:       HK2 ServiceLocator Default Implementation

%description locator
Hundred Kilobytes Kernel ServiceLocator Default Implementation.

%package utils
Summary:       HK2 Implementation Utilities

%description utils
Hundred Kilobytes Kernel Implementation Utilities.

%package javadoc
Summary:       Javadoc for %{pkg_name}

%description javadoc
This package contains javadoc for %{pkg_name}.

%prep

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%setup -q -n hk2-hk2-parent-%{namedversion}
# Do not remove test resources
find . -name '*.jar' ! -name "gendir.jar" -type f -print -delete
find . -name '*.class' -print -delete

%patch0 -p0
%patch1 -p1
%patch2 -p1

%pom_remove_plugin :maven-resources-plugin

# org.apache.maven.wagon:wagon-webdav-jackrabbit:2.0
%pom_xpath_remove pom:build/pom:extensions

%pom_remove_plugin com.googlecode.maven-download-plugin:maven-download-plugin
%pom_remove_plugin :maven-site-plugin
%pom_remove_plugin :maven-eclipse-plugin
%pom_remove_plugin :maven-release-plugin
%pom_remove_plugin :findbugs-maven-plugin

%pom_disable_module external
%pom_remove_dep org.glassfish.hk2.external: bom
%pom_remove_dep org.glassfish.hk2:external bom
%pom_remove_dep org.glassfish.hk2:tiger-types-osgi bom
%pom_disable_module examples
# Use unavailable: org.ops4j.pax.exam, org.ops4j.pax.url
%pom_disable_module osgi-adapter-test osgi/adapter-tests
%pom_remove_dep :osgi-adapter-test bom

%pom_disable_module hk2-maven
%pom_disable_module hk2-inhabitant-generator
%pom_disable_module hk2-metadata-generator
%pom_disable_module consolidatedbundle-maven-plugin
%pom_disable_module hk2-runlevel
%pom_disable_module class-model
%pom_disable_module hk2-core
%pom_disable_module osgi
%pom_disable_module dependency-verifier
%pom_disable_module dependency-visualizer
%pom_disable_module hk2-testing
%pom_disable_module guice-bridge
%pom_disable_module spring-bridge
%pom_disable_module hk2-jmx
%pom_disable_module hk2
%pom_disable_module hk2-configuration
%pom_disable_module hk2-extras

%pom_remove_dep org.ops4j.base:
%pom_remove_dep org.ops4j.pax.exam:
%pom_remove_dep org.ops4j.pax.tipi:
%pom_remove_dep org.ops4j.pax.url:

# disable tiger-types copy
%pom_remove_plugin :maven-dependency-plugin hk2-utils

%pom_xpath_remove "pom:plugin[pom:artifactId ='maven-surefire-plugin']/pom:configuration" hk2-api
%pom_xpath_remove "pom:plugin[pom:artifactId ='maven-surefire-plugin']/pom:configuration" hk2-locator

%pom_remove_dep "org.easymock:easymock"
%pom_xpath_set "pom:dependency[pom:artifactId = 'javax.inject']/pom:groupId" javax.inject hk2-locator

cp -p %{SOURCE1} LICENSE.txt
sed -i 's/\r//' LICENSE.txt

%mvn_package ":osgiversion-maven-plugin" __noinstall
%mvn_package ":hk2-api" api
%mvn_package ":hk2-bom" %{pkg_name}
%mvn_package ":hk2-parent" %{pkg_name}
%mvn_package ":hk2-locator" locator
%mvn_package ":hk2-utils" utils

%{?scl:EOF}

%build

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}

%mvn_build -- -Dmaven.test.skip=true

%{?scl:EOF}

%install

%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
%mvn_install

%{?scl:EOF}

%files -f .mfiles-%{pkg_name}
%dir %{_mavenpomdir}/glassfish-hk2
%doc README.md LICENSE.txt

%files api -f .mfiles-api
%doc LICENSE.txt

%files locator -f .mfiles-locator
%doc LICENSE.txt

%files utils -f .mfiles-utils
%doc LICENSE.txt
%dir %{_javadir}/glassfish-hk2
%dir %{_mavenpomdir}/glassfish-hk2

%files javadoc -f .mfiles-javadoc
%doc LICENSE.txt

%changelog
* Tue Jul 28 2015 Alexander Kurtakov <akurtako@redhat.com> 2.4.0-0.7.3.b25
- Drop obsolete outside of DTS namespace.

* Mon Jul 20 2015 Mat Booth <mat.booth@redhat.com> - 2.4.0-0.7.2.b25
- Fix unowned directories

* Fri Jul 03 2015 Roland Grunberg <rgrunber@redhat.com> - 2.4.0-0.7.1.b25
- SCL-ize.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.0-0.7.b25
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 08 2015 gil cattaneo <puntogil@libero.it> 2.4.0-0.6.b25
- update to 2.4.0-b25

* Wed May 27 2015 gil cattaneo <puntogil@libero.it> 2.4.0-0.5.b24
- generate hk2-inhabitant-generator OSGi manifest

* Mon May 25 2015 gil cattaneo <puntogil@libero.it> 2.4.0-0.4.b24
- fix failure on directory creation

* Mon May 25 2015 gil cattaneo <puntogil@libero.it> 2.4.0-0.3.b24
- enable javadoc sub package

* Mon May 25 2015 gil cattaneo <puntogil@libero.it> 2.4.0-0.2.b24
- remove empty javadoc sub package
 
* Sat May 23 2015 gil cattaneo <puntogil@libero.it> 2.4.0-0.1.b24
- update to 2.4.0-b24

* Mon May 04 2015 gil cattaneo <puntogil@libero.it> 2.3.0-1
- update to 2.3.0

* Fri Feb 27 2015 Michal Srb <msrb@redhat.com> - 2.1.93-9
- Use mvn()-like BRs

* Tue Feb 03 2015 gil cattaneo <puntogil@libero.it> 2.1.93-8
- introduce license macro

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.93-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 09 2014 Michal Srb <msrb@redhat.com> - 2.1.93-6
- Remove BR: apt-maven-plugin

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 2.1.93-5
- Use Requires: java-headless rebuild (#1067528)

* Thu Nov 14 2013 gil cattaneo <puntogil@libero.it> 2.1.93-4
- use objectweb-asm3

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.93-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 10 2013 gil cattaneo <puntogil@libero.it> 2.1.93-2
- switch to XMvn
- minor changes to adapt to current guideline

* Tue May 14 2013 gil cattaneo <puntogil@libero.it> 2.1.93-1
- update to 2.1.93

* Fri Apr 26 2013 gil cattaneo <puntogil@libero.it> 2.1.92-1
- update to 2.1.92

* Sat Oct 13 2012 gil cattaneo <puntogil@libero.it> 2.1.37-1
- update to 2.1.37

* Sat Oct 06 2012 gil cattaneo <puntogil@libero.it> 2.1.35-1
- update to 2.1.35

* Sat Aug 25 2012 gil cattaneo <puntogil@libero.it> 2.1.34-1
- initial rpm
