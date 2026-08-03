subroutine simulate_sail(leaf_refl, leaf_trans, psoil, LAI, hspot, &
                         tts, tto, psi, TypeLidf, LIDFa, LIDFb, result)

	! Run the 4SAIL canopy model on a supplied leaf reflectance/transmittance
	! spectrum, skipping PROSPECT. Mirrors the canopy path in main_PROSAIL.f90
	! `simulate`, but injects the leaf optical properties instead of computing
	! them. 4SAIL scattering math is from Verhoef et al. (2007); the reference
	! implementation lives in PRO4SAIL.f90 (whose Jfunc/volscatt helpers we reuse).

	USE MOD_ANGLE			! pi & rad conversion
	USE MOD_staticvar		! SAIL working arrays + Suits coefficients
	USE MOD_output_PROSPECT	! rho/tau (leaf optics injection point)
	USE MOD_SAIL			! SAIL output reflectance factors
	USE MOD_dataSpec_PDB	! nw, Es, Ed, Rsoil1, Rsoil2
	IMPLICIT NONE

	! DATA INPUTS/OUTPUTS
	REAL*8, intent(in) :: leaf_refl(nw), leaf_trans(nw)
	REAL*8, intent(in) :: psoil, LAI, hspot, tts, tto, psi, LIDFa, LIDFb
	INTEGER, intent(in) :: TypeLidf
	REAL*8, intent(out) :: result(nw)

	! geometry / LIDF loop scalars
	REAL*8 :: chi_o,chi_s,ctl,tanto,tants,cospsi,koli,ksli,bf,bfli
	REAL*8 :: sobli,sofli,ttl,frho,ftau,litab(13)
	! hotspot scalars
	REAL*8 :: alf,f1,f2,x1,x2,y1,y2,z,fhot,fint
	! direct/diffuse weighting
	REAL*8 :: skyl
	! external function
	REAL*8 :: Jfunc3
	! working spectra (automatic arrays, length nw)
	REAL*8 :: sigf(nw),g1(nw),g2(nw)
	REAL*8 :: J1ko(nw),J1ks(nw),J2ko(nw),J2ks(nw)
	REAL*8 :: T1(nw),T2(nw),T3(nw),Tv1(nw),Tv2(nw)
	REAL*8 :: e1(nw),e2(nw),rinf2(nw),re(nw),denom(nw)
	REAL*8 :: Ps(nw),Qs(nw),Pv(nw),Qv(nw),dn(nw)
	REAL*8 :: rsoil0(nw),PARdiro(nw),PARdifo(nw)
	INTEGER*4 :: na
	data litab/5.,15.,25.,35.,45.,55.,65.,75.,81.,83.,85.,87.,89./

	! ANGLE CONVERSION
	pi=ATAN(1.)*4.
	rd=pi/180.

	! allocate the module-level working & output arrays (as `simulate` does)
	ALLOCATE (rho(nw),tau(nw))
	ALLOCATE (sb(nw),sf(nw),vb(nw),vf(nw),w(nw))
	ALLOCATE (m(nw),m2(nw),att(nw),sigb(nw),rinf(nw))
	ALLOCATE (tsd(nw),tdd(nw),tdo(nw),rsd(nw),rdd(nw),rso(nw),rdo(nw))
	ALLOCATE (rddt(nw),rsdt(nw),rdot(nw),rsodt(nw),rsost(nw),rsot(nw),rsos(nw),rsod(nw))
	ALLOCATE (lidf(13))

	! inject the supplied leaf spectrum in place of a PROSPECT call
	rho = leaf_refl
	tau = leaf_trans

	! soil reflectance: psoil=1 dry, psoil=0 wet
	rsoil0 = psoil*Rsoil1 + (1-psoil)*Rsoil2

	! Geometric quantities
	cts		= COS(rd*tts)
	cto		= COS(rd*tto)
	ctscto	= cts*cto
	tants	= TAN(rd*tts)
	tanto	= TAN(rd*tto)
	cospsi	= COS(rd*psi)
	dso		= SQRT(tants*tants+tanto*tanto-2.*tants*tanto*cospsi)

	! Leaf angle distribution: (a,b) parameters or ellipsoidal mean angle
	na=13
	IF(TypeLidf.EQ.1) THEN
		CALL dladgen(LIDFa,LIDFb,lidf)
	ELSEIF(TypeLidf.EQ.2) THEN
		CALL calc_LIDF_ellipsoidal(na,LIDFa,lidf)
	ENDIF

	! Geometric factors for extinction and scattering, summed over the LIDF
	ks	= 0
	ko	= 0
	bf	= 0
	sob	= 0
	sof	= 0
	DO i=1,na
		ttl = litab(i)
		ctl = COS(rd*ttl)
		CALL volscatt(tts,tto,psi,ttl,chi_s,chi_o,frho,ftau)
		ksli	= chi_s/cts
		koli	= chi_o/cto
		sobli	= frho*pi/ctscto
		sofli	= ftau*pi/ctscto
		bfli	= ctl*ctl
		ks	= ks+ksli*lidf(i)
		ko	= ko+koli*lidf(i)
		bf	= bf+bfli*lidf(i)
		sob	= sob+sobli*lidf(i)
		sof	= sof+sofli*lidf(i)
	ENDDO
	sdb	= 0.5*(ks+bf)
	sdf	= 0.5*(ks-bf)
	dob	= 0.5*(ko+bf)
	dof	= 0.5*(ko-bf)
	ddb	= 0.5*(1.+bf)
	ddf	= 0.5*(1.-bf)

	! Here rho and tau come in (Suits coefficients)
	sigb= ddb*rho+ddf*tau
	sigf= ddf*rho+ddb*tau
	att	= 1.-sigf
	m2=(att+sigb)*(att-sigb)
	WHERE (m2.LT.0)
		m2=0
	ENDWHERE
	m=SQRT(m2)
	sb	= sdb*rho+sdf*tau
	sf	= sdf*rho+sdb*tau
	vb	= dob*rho+dof*tau
	vf	= dof*rho+dob*tau
	w	= sob*rho+sof*tau

	IF (lai.le.0) THEN
		! bare soil: only rdot/rsot feed the weighting below
		rdot	= rsoil0
		rsot	= rsoil0
	ELSE
		! Here the LAI comes in
		e1		= EXP(-m*lai)
		e2		= e1*e1
		rinf	= (att-m)/sigb
		rinf2	= rinf*rinf
		re		= rinf*e1
		denom	= 1.-rinf2*e2

		CALL Jfunc1(ks,m,lai,J1ks)
		CALL Jfunc2(ks,m,lai,J2ks)
		CALL Jfunc1(ko,m,lai,J1ko)
		CALL Jfunc2(ko,m,lai,J2ko)

		Ps = (sf+sb*rinf)*J1ks
		Qs = (sf*rinf+sb)*J2ks
		Pv = (vf+vb*rinf)*J1ko
		Qv = (vf*rinf+vb)*J2ko

		rdd	= rinf*(1.-e2)/denom
		tdd	= (1.-rinf2)*e1/denom
		tsd	= (Ps-re*Qs)/denom
		rsd	= (Qs-re*Ps)/denom
		tdo	= (Pv-re*Qv)/denom
		rdo	= (Qv-re*Pv)/denom

		tss	= EXP(-ks*lai)
		too	= EXP(-ko*lai)
		z	= Jfunc3(ks,ko,lai)
		g1	= (z-J1ks*too)/(ko+m)
		g2	= (z-J1ko*tss)/(ks+m)

		Tv1 = (vf*rinf+vb)*g1
		Tv2 = (vf+vb*rinf)*g2
		T1	= Tv1*(sf+sb*rinf)
		T2	= Tv2*(sf*rinf+sb)
		T3	= (rdo*Qs+tdo*Ps)*rinf

		! Multiple scattering contribution to bidirectional canopy reflectance
		rsod = (T1+T2-T3)/(1.-rinf2)

		! Treatment of the hotspot-effect
		alf=1e6
		IF (hspot.gt.0.) THEN
			alf=(dso/hspot)*2./(ks+ko)
		ENDIF
		IF (alf.GT.200.) THEN
			alf=200.
		ENDIF
		IF (alf.eq.0.) THEN
			! The pure hotspot - no shadow
			tsstoo = tss
			sumint = (1-tss)/(ks*lai)
		ELSE
			! Outside the hotspot
			fhot=lai*SQRT(ko*ks)
			! Integrate by exponential Simpson method in 20 steps
			x1=0.
			y1=0.
			f1=1.
			fint=(1.-EXP(-alf))*.05
			sumint=0.
			DO i=1,20
				IF (i.lt.20) THEN
					x2=-LOG(1.-i*fint)/alf
				ELSE
					x2=1.
				ENDIF
				y2=-(ko+ks)*lai*x2+fhot*(1.-EXP(-alf*x2))/alf
				f2=EXP(y2)
				sumint=sumint+(f2-f1)*(x2-x1)/(y2-y1)
				x1=x2
				y1=y2
				f1=f2
			ENDDO
			tsstoo=f1
		ENDIF

		! Single scattering contribution
		rsos = w*lai*sumint
		! Total canopy contribution
		rso=rsos+rsod

		! Interaction with the soil
		dn=1.-rsoil0*rdd
		rddt=rdd+tdd*rsoil0*tdd/dn
		rsdt=rsd+(tsd+tss)*rsoil0*tdd/dn
		rdot=rdo+tdd*rsoil0*(tdo+too)/dn
		rsodt=rsod+((tss+tsd)*tdo+(tsd+tss*rsoil0*rdd)*too)*rsoil0/dn
		rsost=rsos+tsstoo*rsoil0
		rsot=rsost+rsodt
	ENDIF

	! direct / diffuse light weighting (Francois et al. 2002)
	skyl	= 0.847- 1.61*sin((90-tts)*rd)+ 1.04*sin((90-tts)*rd)*sin((90-tts)*rd)
	PARdiro	= (1-skyl)*Es
	PARdifo	= (skyl)*Ed
	result	= (rdot*PARdifo+rsot*PARdiro)/(PARdiro+PARdifo)

	! clean up
	DEALLOCATE(rho,tau)
	DEALLOCATE(sb,sf,vb,vf,w)
	DEALLOCATE(m,m2,att,sigb,rinf)
	DEALLOCATE(tsd,tdd,tdo,rsd,rdd,rso,rdo)
	DEALLOCATE(rddt,rsdt,rdot,rsodt,rsost,rsot,rsos,rsod)
	DEALLOCATE(lidf)

END
